from .views import AllGroupList, GroupUpdateDelete, AddGroupMember, RemoveMember, ChangeAdmin, GetGroupDetails, \
    AddFriendMember

from django.urls import path

urlpatterns = [
    path('list/', AllGroupList.as_view(), name='list_create_group'),
    path('edit-delete/<int:pk>/', GroupUpdateDelete.as_view(), name='group-edit-delete'),
    path('add-member/', AddGroupMember.as_view(), name='add-member'),
    path('remove-member/', RemoveMember.as_view(), name='remove-member'),
    path('change-admin/', ChangeAdmin.as_view(), name='change-admin'),
    path('details/', GetGroupDetails.as_view(), name='group-details'),
    path('add-friend-member/', AddFriendMember.as_view(), name='add-friend-member'),

    # path('create_group/', create_group, name='create_group'),
    # path('edit_group/<int:g_id>', edit_group, name='edit_group'),
    # path('add_Member/', addMember, name='addMember'),
    # path('deleteMember/', deleteMember, name='deleteMember'),
    # path('makeAdmin/', makeAdmin, name='makeAdmin'),
    # path('search_Members/', searchMembers, name='searchMembers'),
    # path('addFriendMember/', addFriendMember, name='addFriendMember'),
    # path('getMemberOfGroup/', getMemberOfGroup, name='getMemberOfGroup'),

]
