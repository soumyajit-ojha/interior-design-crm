"""
This file defines the URL patterns for the users application.

It maps URL paths to corresponding views, allowing users to interact with the application.

"""

from django.urls import path
from users.views import (
    UserList,
    UserDetail,
    LoginView,
    ClientCreateAPIView,
    ClientLoginView,
    UpdateUserDetail,
    UpdateNewPassword,
    ClientVideoDetail,
    UserQueryCreatAPIView,
    UserQueryRetrieveAPIView,
    ForgotPasswordView,
    ResetPasswordConfirmView,
    CustomTokenRefreshView,
    ResetPasswordValidateLinkView,
    UserListByTypeAPIView,
)

# ExportExcel,ExportPDF,SendOtpVerification

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("users_list/", UserList.as_view(), name="users_list"),
    path("users_detail/<int:pk>/", UserDetail.as_view(), name="users_detail"),
    path("create_client/", ClientCreateAPIView.as_view(), name="create_client"),
    path("login_client/", ClientLoginView.as_view(), name="login_client"),
    path("update_client/<int:pk>/", UpdateUserDetail.as_view(), name="update_client"),
    path(
        "update_password/<int:pk>/", UpdateNewPassword.as_view(), name="update_password"
    ),
    path("client_videos/", ClientVideoDetail.as_view(), name="client_video"),
    # path("query/", UserQueryCreatAPIView.as_view(), name="user_query"),
    # path("query_get/", UserQueryRetrieveAPIView.as_view(), name="user_query"),
    # path('export/pdf/<int:pk>/', ExportPDF.as_view(), name='export_pdf'),
    # path('export/excel/<int:pk>/', ExportExcel.as_view(), name='export_excel'),
    # path('send-otp/', SendOtpVerification.as_view(), name='send_otp'),
    path("forgot_password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path(
        "reset_password/validate/<str:uid>/<str:token>/",
        ResetPasswordValidateLinkView.as_view(),
        name="validate_reset_password_link",
    ),
    path("reset_password/", ResetPasswordConfirmView.as_view(), name="reset_password"),
    path("refresh_token/", CustomTokenRefreshView.as_view(), name="refresh_token"),
    path("by-type/", UserListByTypeAPIView.as_view(), name="users-by-type"),
]
