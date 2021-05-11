from view_builder.model.dataset import (
    DatasetModel,
    DatasetModelFactory,
    DeveloperAgreementTypeModel,
    LocalAuthorityDistrictModel,
    DevelopmentPolicyModel,
    DevelopmentPlanDocumentModel,
    DocumentModel,
)
from view_builder.model.table import (
    Slug,
    Organisation,
    Geography,
    OrganisationGeography,
    Category,
    Policy,
    PolicyOrganisation,
    PolicyGeography,
    PolicyDocument,
    PolicyCategory,
    Document,
    DocumentGeography,
    DocumentOrganisation,
    DocumentCategory,
)
import datetime
import pytest


class DummyModel:
    dataset_name = "dummy-dataset"

    def __init__(self, *args):
        pass


dummy_organisation = Organisation(
    id=1, organisation="government-organisation:CCC", name="some organisation"
)
dummy_geography = Geography(
    id=1, geography="government-geography:A000000", name="some geography"
)
dummy_category = Category(id=1, category="A category", name="some category")
dummy_policy = Policy(id=1, policy="A policy", name="some policy")
dummy_slug = Slug(id=1, slug="/a/slug/example")


@pytest.fixture
def mock_get_organisation(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_organisation",
        lambda self, org: dummy_organisation,
    )
    return mock_db


@pytest.fixture
def mock_get_geography(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_geography",
        lambda self, geography: dummy_geography,
    )
    return mock_db


@pytest.fixture
def mock_get_category(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_category",
        lambda self, category, type: dummy_category,
    )
    return mock_db


@pytest.fixture
def mock_get_policy(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_policy",
        lambda self, policy: dummy_policy,
    )
    return mock_db


@pytest.fixture
def mock_get_slug(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_slug",
        lambda self, slug: dummy_slug,
    )
    return mock_db


def test_dataset_model_factory_register_and_get():
    test_factory = DatasetModelFactory()
    test_factory.register_dataset_model(DummyModel)
    output = test_factory.get_dataset_model("dummy-dataset", None, {"check": True})

    assert isinstance(output, DummyModel)


def test_dataset_model_factory_no_class():
    test_factory = DatasetModelFactory()
    with pytest.raises(ValueError, match="^No matching dataset model found$"):
        test_factory.get_dataset_model("test_class", None, {"check": True})


def test_dataset_model_date_mapping():
    test_data = {
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "slug": "dataset/AAA",
    }
    DatasetModel(None, test_data)


def test_dataset_model_no_slug():
    test_data = {"entry-date": "2020-10-04", "start-date": "2020-10-05"}

    with pytest.raises(ValueError, match="^Data missing slug field$"):
        DatasetModel(None, test_data)


def test_dataset_model_no_entry_date():
    test_data = {"start-date": "2020-10-05", "slug": "dataset/AAA"}

    with pytest.raises(ValueError, match="^Entry missing entry-date$"):
        DatasetModel(None, test_data)


def test_dataset_model_future_entry_date():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    test_data = {
        "entry-date": tomorrow.isoformat(),
        "start-date": "2020-10-05",
        "slug": "dataset/AAA",
    }

    with pytest.raises(ValueError, match="^entry-date cannot be in the future$"):
        DatasetModel(None, test_data)


# Test to cover CategoryDatasetModel
def test_development_agreement_type_model():
    test_data = {
        "developer-agreement-type": "AAA",
        "name": "BBB",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "slug": "developer-agreement-type/AAA",
        "extra_field": "CCC",
    }

    developer_agreement_type_orm = DeveloperAgreementTypeModel(None, test_data)
    orm_obj_list = developer_agreement_type_orm.to_orm()

    assert len(orm_obj_list) == 1
    orm_obj = orm_obj_list[0]

    assert orm_obj.name == test_data["name"]
    assert orm_obj.start_date == test_data["start_date"]
    assert orm_obj.slug.slug == test_data["slug"]


def test_local_authority_district_model(mocker):
    test_data = {
        "name": "BBB",
        "geography": "local-authority-district:AAA",
        "geometry": "MULTIPOLYGON (((-1.111111 2.222222, 3.333333333 4.444444444)))",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisation": "government-organisation:CCC",
        "slug": "local-authority-district/AAA",
        "extra_field": "ZZZ",
    }
    test_organisation = Organisation(
        id=1, organisation="government-organisation:CCC", name="some organisation"
    )
    mocker.patch(
        "view_builder.model.dataset.LocalAuthorityDistrictModel.get_organisation",
        lambda self, org: test_organisation,
    )
    local_authority_district_orm = LocalAuthorityDistrictModel(None, test_data)
    orm_obj_list = local_authority_district_orm.to_orm()

    assert len(orm_obj_list) == 2
    first_orm_obj = orm_obj_list[0]

    assert isinstance(first_orm_obj, Geography)
    assert first_orm_obj.geography == test_data["geography"]
    assert first_orm_obj.geometry == test_data["geometry"]
    assert first_orm_obj.slug.slug == test_data["slug"]

    second_orm_obj = orm_obj_list[1]
    assert isinstance(second_orm_obj, OrganisationGeography)
    assert second_orm_obj.geography == first_orm_obj
    assert second_orm_obj.organisation == test_organisation


@pytest.mark.usefixtures("mock_get_organisation")
@pytest.mark.usefixtures("mock_get_geography")
@pytest.mark.usefixtures("mock_get_category")
def test_development_policy_model(
    mock_get_organisation, mock_get_geography, mock_get_category
):
    test_data = {
        "development-policy": "AAA",
        "name": "BBB",
        "development-policy-categories": "A;B",
        "geographies": "A000000;B1111111",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisation": "government-organisation:CCC",
        "slug": "/development-policy/local-authority-eng/CCC/AAA",
        "notes": "ZZZ",
        "description": "a description",
    }

    development_policy_orm = DevelopmentPolicyModel(None, test_data)
    orm_obj_list = development_policy_orm.to_orm()

    assert len(orm_obj_list) == 6

    first_orm_obj = orm_obj_list[0]
    assert isinstance(first_orm_obj, Policy)
    assert first_orm_obj.policy == test_data["development-policy"]
    assert first_orm_obj.name == test_data["name"]
    assert first_orm_obj.notes == test_data["notes"]
    assert first_orm_obj.description == test_data["description"]
    assert first_orm_obj.slug.slug == test_data["slug"]

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyCategory)
                and x.category == dummy_category
                and x.policy == first_orm_obj
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyOrganisation)
                and x.policy == first_orm_obj
                and x.organisation == dummy_organisation
            ]
        )
        == 1
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyGeography)
                and x.policy == first_orm_obj
                and x.geography == dummy_geography
            ]
        )
        == 2
    )


@pytest.mark.usefixtures("mock_get_organisation")
@pytest.mark.usefixtures("mock_get_geography")
@pytest.mark.usefixtures("mock_get_category")
@pytest.mark.usefixtures("mock_get_policy")
def test_development_plan_document_model(
    mock_get_organisation, mock_get_geography, mock_get_category, mock_get_policy
):
    test_data = {
        "development-plan-document": "AAA",
        "name": "BBB",
        "development-plan-types": "A;B",
        "development-policies": "pol-a;pol-b",
        "geographies": "A000000;B1111111",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisations": "government-organisation:CCC",
        "document-url": "www.example.com",
        "slug": "/development-plan-document/local-authority-eng/CCC/AAA",
        "notes": "ZZZ",
        "description": "a description",
    }

    development_plan_doc_orm = DevelopmentPlanDocumentModel(None, test_data)
    orm_obj_list = development_plan_doc_orm.to_orm()

    assert len(orm_obj_list) == 8

    first_orm_obj = orm_obj_list[0]
    assert isinstance(first_orm_obj, Document)
    assert first_orm_obj.document == test_data["development-plan-document"]
    assert first_orm_obj.name == test_data["name"]
    assert first_orm_obj.notes == test_data["notes"]
    assert first_orm_obj.description == test_data["description"]
    assert first_orm_obj.slug.slug == test_data["slug"]
    assert first_orm_obj.document_url == test_data["document-url"]

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentCategory)
                and x.document == first_orm_obj
                and x.category == dummy_category
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyDocument)
                and x.document == first_orm_obj
                and x.policy == dummy_policy
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentOrganisation)
                and x.document == first_orm_obj
                and x.organisation == dummy_organisation
            ]
        )
        == 1
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentGeography)
                and x.document == first_orm_obj
                and x.geography == dummy_geography
            ]
        )
        == 2
    )


@pytest.fixture
def mock_get_geography_slug(mocker):
    ret = dummy_slug
    ret.geography = [dummy_geography]
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_slug",
        lambda self, slug: ret,
    )
    return mock_db


@pytest.mark.usefixtures("mock_get_organisation")
@pytest.mark.usefixtures("mock_get_geography_slug")
@pytest.mark.usefixtures("mock_get_category")
@pytest.mark.usefixtures("mock_get_policy")
def test_document_model(
    mock_get_organisation, mock_get_geography_slug, mock_get_category, mock_get_policy
):
    test_data = {
        "document": "AAA",
        "name": "BBB",
        "document-types": "A;B",
        "development-policies": "pol-a;pol-b",
        "geographies": "/a/slug/example;/a/slug/example/b",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisations": "local-authority-eng:CCC",
        "document-url": "www.example.com",
        "slug": "/document/area/CCC/AAA",
        "notes": "ZZZ",
        "description": "a description",
    }

    doc_orm = DocumentModel(None, test_data)
    orm_obj_list = doc_orm.to_orm()

    assert len(orm_obj_list) == 8

    first_orm_obj = orm_obj_list[0]
    assert isinstance(first_orm_obj, Document)
    assert first_orm_obj.document == test_data["document"]
    assert first_orm_obj.name == test_data["name"]
    assert first_orm_obj.notes == test_data["notes"]
    assert first_orm_obj.description == test_data["description"]
    assert first_orm_obj.slug.slug == test_data["slug"]
    assert first_orm_obj.document_url == test_data["document-url"]

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentCategory)
                and x.document == first_orm_obj
                and x.category == dummy_category
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyDocument)
                and x.document == first_orm_obj
                and x.policy == dummy_policy
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentOrganisation)
                and x.document == first_orm_obj
                and x.organisation == dummy_organisation
            ]
        )
        == 1
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentGeography)
                and x.document == first_orm_obj
                and x.geography == dummy_geography
            ]
        )
        == 2
    )
