
from django.urls import path
from .views import CSVUploadView, CSVOperationView, TaskStatusView

urlpatterns = [
    path('upload-csv/', CSVUploadView.as_view(), name='upload-csv'),
    path('perform-operation/', CSVOperationView.as_view(), name='perform-operation'),
    path('task-status/', TaskStatusView.as_view(), name='task-status'),
]
