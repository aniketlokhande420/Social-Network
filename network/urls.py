from django.urls import path, include
from .views import (WelcomeView,
    SignUpView, LoginView, UserSearchView,
    SendFriendRequestView, RespondFriendRequestView,
    ListFriendsView, ListPendingRequestsView
)

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/respond/<int:pk>/<str:action>/', RespondFriendRequestView.as_view(), name='respond-friend-request'),
    path('friends/', ListFriendsView.as_view(), name='list-friends'),
    path('friend-requests/pending/', ListPendingRequestsView.as_view(), name='pending-friend-requests'),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]