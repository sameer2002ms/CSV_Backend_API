from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CSVFile
from .serializers import CSVFileSerializer
from celery.result import AsyncResult
from .tasks import process_csv_task

class CSVUploadView(APIView):
    def post(self, request):
        serializer = CSVFileSerializer(data=request.data)
        if serializer.is_valid():
            csv_file = serializer.save()
            return Response({"message": "File uploaded successfully", "file_id": str(csv_file.id)}, status=status.HTTP_201_CREATED)
        return Response({"error": "Invalid file formatformat. Only CSV files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

class CSVOperationView(APIView):
    def post(self, request):
        file_id = request.data.get('file_id')
        operation = request.data.get('operation')
        column = request.data.get('column')# Optional for unique operation
        filters = request.data.get('filters')  # Retrieve filtering conditions if provided

        if not file_id or not operation:
            return Response({"error": "file_id and operation are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            csv_file = CSVFile.objects.get(id=file_id)
        except CSVFile.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        if operation not in ["dedup", "unique","filter"]:
            return Response({"error": "Invalid operation or file not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Start the task using Celery
        task = process_csv_task.delay(csv_file.file.path, operation, column, filters)
        
        # Extract the task_id from the AsyncResult object
        return Response({"message": "Operation started", "task_id": task.id}, status=status.HTTP_200_OK)


class TaskStatusView(APIView):
    def get(self, request, *args, **kwargs):
        # Get task_id from query parameters
        task_id = request.GET.get('task_id')
        n = request.GET.get('n', 100)  # Default to 100 if 'n' is not provided

        # If task_id is missing, return an error
        if not task_id:
            return Response({"error": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the task result using the task_id
        task_result = AsyncResult(task_id)
        
        if not task_result.task_id or task_result.state == 'REVOKED':
            return Response({"error": "Invalid task ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Check task status
        if task_result.state == 'PENDING':
            return Response({
                "task_id": task_id,
                "status": "PENDING"
            }, status=status.HTTP_200_OK)

        elif task_result.state == 'SUCCESS':
            result = task_result.result
            if result is None or not isinstance(result,dict):
                return Response({
                    "task_id": task_id,
                    "status": "SUCCESS",
                    "result": "Task completed, but no result data available."
                }, status=status.HTTP_200_OK)
            # Assuming the result is a list of rows, truncate it based on 'n'
            result_data = task_result.result.get('data', [])[:int(n)]
            file_link = task_result.result.get('file_link', '')

            return Response({
                "task_id": task_id,
                "status": "SUCCESS",
                "result": {
                    "data": result_data,
                    "file_link": file_link
                }
            }, status=status.HTTP_200_OK)

        elif task_result.state == 'FAILURE':
            return Response({
                "task_id": task_id,
                "status": "FAILURE",
                "error": str(task_result.info)
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "task_id": task_id,
                "status": task_result.state
            }, status=status.HTTP_200_OK)




