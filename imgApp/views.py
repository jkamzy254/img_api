from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view

    
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.db import connection
import datetime, json, pandas as pd
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv, find_dotenv
import base64
import requests

load_dotenv(find_dotenv())

# Create your views here.


class UploadImageViewSet(APIView):
    
    # def add_ticket(id, data):
    #     print("In the ticket area")
        
    #     e, arr = data

    #     user_list = ["5fc6aa25facfd6007632ccfa", "5f9020eff162650070c78aa8"]  # Scott and Kamau
    #     random_user = random.choice(user_list)

    #     # Prepare description based on `e`
    #     if 'rectype' in e:
    #         description = f"{e['rectype']}: {e['record']}\n\n{e['description']}\n\nUID: {e['uid']}"
    #     else:
    #         description = e['description']
        
    #     print(e)

    #     issue_data = {
    #         "fields": {
    #             "summary": e['subject'],
    #             "issuetype": {
    #                 "id": e['type']
    #             },
    #             "project": {
    #                 "key": "DTT"
    #             },
    #             "assignee": {
    #                 "accountId": random_user
    #             },
    #             "description": {
    #                 "type": "doc",
    #                 "version": 1,
    #                 "content": [
    #                     {
    #                         "type": "paragraph",
    #                         "content": [
    #                             {
    #                                 "type": "text",
    #                                 "text": description
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             },
    #         }
    #     }

    #     try:
    #         # Authenticate and create the ticket
    #         credentials = base64.b64encode(f"{os.getenv('JIRA_USERNAME')}:{os.getenv('TICKET_TOKEN')}".encode('utf-8')).decode('utf-8')
    #         jira_url = f"https://{os.getenv('JIRA_URL')}/rest/api/3/issue"
    #         headers = {
    #             'Authorization': f'Basic {credentials}',
    #             'Accept': 'application/json',
    #             'Content-Type': 'application/json'
    #         }

    #         res = requests.post(jira_url, json=issue_data, headers=headers)
    #         res.raise_for_status()  # Raise an exception for HTTP errors

    #         response_data = res.json()
    #         jira_id = response_data['id']

    #         # Insert Jira ID and timestamp into the SQL database
    #         # Attach files if any
    #         if arr:
    #             attach_url = f"https://{os.getenv('JIRA_URL')}/rest/api/3/issue/{jira_id}/attachments"
    #             for file in arr:
    #                 form_data = {'file': file}  # Handle file here as needed (InMemoryUploadedFile or similar)

    #                 headers = {
    #                     'Authorization': f'Basic {credentials}',
    #                     'X-Atlassian-Token': 'no-check',
    #                 }
    #                 files = {'file': (file.name, file.read())}
    #                 response = requests.post(attach_url, headers=headers, files=files)
    #                 response.raise_for_status()

    #         return response_data

    #     except requests.exceptions.RequestException as error:
    #         print(f"Error creating Jira ticket: {error}")
    #         raise error
    
    def post(self, request):
        print("Request Received")
        upload_file = request.FILES.get('profileImage')
        date_time = datetime.datetime.now()
        epoch_time = int(date_time.timestamp())
        uid = 'A006Z'

        if not upload_file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create a BlobServiceClient using the connection string
            blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_STORAGE_CONNECTION_STRING'))

            # Get the container client
            container_client = blob_service_client.get_container_client(os.environ.get('TICKET_CONTAINER'))

            # Upload the file to Azure Blob Storage
            blob_client = container_client.get_blob_client(uid+str(epoch_time)+upload_file.name)
            blob_client.upload_blob(upload_file.read(), overwrite=True)
            image_url = blob_client.url
            
            resp = {
                'message': 'File uploaded successfully to Azure Blob Storage.',
                'imglink': image_url
            }

            return Response(resp, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)