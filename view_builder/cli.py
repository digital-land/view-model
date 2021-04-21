import click
from digital_land.model.entity import Entity
from digital_land.repository.entry_repository import EntryRepository
from view_builder.builder import ViewBuilder
from view_builder.model.dataset import factory as dataset_model_factory

from view_builder.model.table import Base
from sqlalchemy import create_engine


@click.group()
def cli():
    pass


@click.command("build", short_help="build the view model for a single dataset")
@click.argument("dataset_name", type=click.STRING)
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
def build(dataset_name, input_path, output_path):
    entry_repo = EntryRepository(input_path)
    entities = entry_repo.list_entities()
    reader = (
        Entity(entry_repo.find_by_entity(entity)).snapshot() for entity in entities
    )
    engine = create_engine("sqlite+pysqlite:///{}".format(output_path))
    builder = ViewBuilder(
        engine=engine,
        item_mapper=lambda name, item: dataset_model_factory.get_dataset_model(
            name, item
        ).to_orm(),
    )
    builder.init_model(Base.metadata)
    builder.build_model(dataset_name, reader)


cli.add_command(build)
