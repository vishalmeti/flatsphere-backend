# workspaces/urls.py (no changes needed)
from django.urls import path, include
from . import views

urlpatterns = [
    # Workspace URLs
    path(
        "list/",
        views.WorkspaceViewSet.as_view(
            {"get": "list_workspaces", "post": "create_workspace"}
        ),
    ),
    path(
        "<int:pk>/",
        views.WorkspaceViewSet.as_view(
            {
                "get": "retrieve_workspace",
                "patch": "update_workspace",
                "delete": "delete_workspace",
            }
        ),
    ),
    # UserWorkspace URLs
    path(
        "<int:workspace_id>/users/",
        views.UserWorkspaceViewSet.as_view(
            {
                "get": "list_user_workspaces",
                "post": "create_user_workspace",
            }
        ),
    ),
    path(
        "<int:workspace_id>/users/<int:pk>/",
        views.UserWorkspaceViewSet.as_view(
            {
                "get": "retrieve_user_workspace",
                "patch": "update_user_workspace",
                "delete": "delete_user_workspace",
            }
        ),
    ),
    # ApartmentUnit URLs
    path(
        "<int:workspace_id>/units/",
        views.ApartmentUnitViewSet.as_view(
            {
                "get": "list_apartment_units",
                "post": "create_apartment_unit",
            }
        ),
    ),
    path(
        "<int:workspace_id>/units/<int:pk>/",
        views.ApartmentUnitViewSet.as_view(
            {
                "get": "retrieve_apartment_unit",
                "patch": "update_apartment_unit",
                "delete": "delete_apartment_unit",
            }
        ),
    ),
    # UserApartment URLs
    path(
        "<int:workspace_id>/units/<int:unit_id>/users/",
        views.UserApartmentViewSet.as_view(
            {
                "get": "list_user_apartments",
                "post": "create_user_apartment",
                "delete": "delete_user_apartment",
            }
        ),
    ),
    # path(
    #     "<int:workspace_id>/units/<int:unit_id>/users/<int:pk>/",
    #     views.UserApartmentViewSet.as_view(
    #         {
    #             # "get": "retrieve_user_apartment",
    #             # "put": "update_user_apartment",
    #             # "patch": "partial_update_user_apartment",
    #             # "delete": "delete_user_apartment",
    #         }
    #     ),
    # ),
]
