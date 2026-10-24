from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema

from tasks.models.internal_task import (
    InternalTask,
    InternalTaskDeadline,
)

from tasks.models.internal_task_attachment import (
    InternalTaskAttachment,
)

from .serializers import (
    InternalTaskSerializer,
    InternalTaskWriteSerializer,
    InternalTaskDeadlineSerializer,
    InternalTaskAttachmentSerializer,
    InternalTaskDeadlineUpdateSerializer,
    InternalTaskDeadlinePatchSerializer,
    InternalTaskCancelSerializer,
    InternalTaskCompleteSerializer,
    InternalTaskReopenSerializer,
    InternalTaskActivateSerializer,
    InternalTaskDeactivateSerializer,
)

from tasks.services.internal_task import (
    finalize_internal_task,
    reopen_internal_task,
    activate_internal_task,
    deactivate_internal_task,
)

from access.internal_task import InternalTaskAccess

from access.permissions import (
    InternalTaskPermission,
    InternalTaskModifyPermission,
)


class InternalTaskListView(
    generics.ListAPIView
):

    search_fields = (
        "title",
        "description",
    )

    serializer_class = InternalTaskSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        return InternalTaskAccess.get_queryset(
            self.request.user
        )


class InternalTaskCreateView(
    generics.CreateAPIView
):

    serializer_class = InternalTaskWriteSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):

        serializer.save(
            created_by=self.request.user
        )


class InternalTaskRetrieveView(
    generics.RetrieveAPIView
):

    serializer_class = InternalTaskSerializer

    permission_classes = [
        IsAuthenticated,
        InternalTaskPermission,
    ]

    def get_queryset(self):

        return InternalTaskAccess.get_queryset(
            self.request.user
        )


class InternalTaskUpdateView(
    generics.UpdateAPIView
):

    serializer_class = InternalTaskWriteSerializer

    permission_classes = [
        IsAuthenticated,
        InternalTaskModifyPermission,
    ]

    def get_queryset(self):

        return InternalTaskAccess.get_queryset(
            self.request.user
        )


class InternalTaskDestroyView(
    generics.DestroyAPIView
):

    permission_classes = [
        IsAuthenticated,
        InternalTaskModifyPermission,
    ]

    def get_queryset(self):

        return InternalTaskAccess.get_queryset(
            self.request.user
        )


class InternalTaskActivateView(
    generics.GenericAPIView
):

    serializer_class = InternalTaskActivateSerializer

    permission_classes = [
        IsAuthenticated,
        InternalTaskModifyPermission,
    ]

    def get_queryset(self):

        return InternalTaskAccess.get_queryset(
            self.request.user
        )

    def post(self, request, pk):

        task = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        self.check_object_permissions(
            request,
            task,
        )

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:

            task = activate_internal_task(
                task=task,
            )

        except ValueError as exc:

            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            InternalTaskSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


class InternalTaskDeactivateView(
    generics.GenericAPIView
):

    serializer_class = InternalTaskDeactivateSerializer

    permission_classes = [
        IsAuthenticated,
        InternalTaskModifyPermission,
    ]

    def get_queryset(self):

        return InternalTaskAccess.get_queryset(
            self.request.user
        )

    def post(self, request, pk):

        task = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        self.check_object_permissions(
            request,
            task,
        )

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:

            task = deactivate_internal_task(
                task=task,
            )

        except ValueError as exc:

            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            InternalTaskSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


class InternalTaskDeadlineDetailView(
    generics.GenericAPIView
):

    serializer_class = InternalTaskDeadlineSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, pk):

        task = get_object_or_404(
            InternalTask,
            pk=pk,
        )

        deadline = get_object_or_404(
            InternalTaskDeadline,
            task=task,
        )

        serializer = self.get_serializer(
            deadline
        )

        return Response(
            serializer.data
        )


class InternalTaskDeadlinePatchView(
    generics.GenericAPIView
):

    serializer_class = (
        InternalTaskDeadlinePatchSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def patch(self, request, pk):

        task = get_object_or_404(
            InternalTask,
            pk=pk,
        )

        deadline, created = (
            InternalTaskDeadline.objects
            .get_or_create(
                task=task,
            )
        )

        serializer = self.get_serializer(
            deadline,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            InternalTaskDeadlineSerializer(
                deadline
            ).data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )


class InternalTaskDeadlineUpdateView(
    generics.GenericAPIView
):

    serializer_class = (
        InternalTaskDeadlineUpdateSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def put(self, request, pk):

        task = get_object_or_404(
            InternalTask,
            pk=pk,
        )

        deadline, created = (
            InternalTaskDeadline.objects
            .get_or_create(
                task=task,
            )
        )

        serializer = self.get_serializer(
            deadline,
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            InternalTaskDeadlineSerializer(
                deadline
            ).data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )


class InternalTaskDeadlineDeleteView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    def delete(self, request, pk):

        task = get_object_or_404(
            InternalTask,
            pk=pk,
        )

        deadline = get_object_or_404(
            InternalTaskDeadline,
            task=task,
        )

        deadline.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )



@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "note": {
                    "type": "string",
                    "description": "یادداشت مربوط به فایل‌ها",
                },
            },
            "required": ["files"],
        },
    },
    responses={
        201: InternalTaskAttachmentSerializer(
            many=True
        ),
    },
)
class InternalTaskAttachmentCreateView(
    generics.CreateAPIView
):

    serializer_class = (
        InternalTaskAttachmentSerializer
    )

    permission_classes = [
        IsAuthenticated,
        InternalTaskPermission,
    ]

    def get_object(self):

        task = get_object_or_404(
            InternalTaskAccess.get_queryset(
                self.request.user
            ),
            pk=self.kwargs["pk"],
        )

        self.check_object_permissions(
            self.request,
            task,
        )

        return task

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        task = self.get_object()

        files = request.FILES.getlist(
            "files"
        )

        note = request.data.get(
            "note",
            "",
        )

        if not files:

            serializer = self.get_serializer(
                data={
                    "note": note,
                }
            )

            serializer.is_valid(
                raise_exception=True
            )

            attachment = serializer.save(
                task=task,
                uploaded_by=request.user,
            )

            return Response(
                self.get_serializer(
                    attachment
                ).data,
                status=status.HTTP_201_CREATED,
            )

        attachments = []

        for file in files:

            serializer = self.get_serializer(
                data={
                    "file": file,
                    "note": note,
                }
            )

            serializer.is_valid(
                raise_exception=True
            )

            attachments.append(
                serializer.save(
                    task=task,
                    uploaded_by=request.user,
                )
            )

        return Response(
            self.get_serializer(
                attachments,
                many=True,
            ).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    responses={
        204: None,
    },
)
class InternalTaskAttachmentDestroyView(
    generics.DestroyAPIView
):

    permission_classes = [
        IsAuthenticated,
        InternalTaskPermission,
    ]

    def get_object(self):

        attachment = get_object_or_404(
            InternalTaskAttachment,
            pk=self.kwargs["attachment_pk"],
            task_id=self.kwargs["pk"],
        )

        self.check_object_permissions(
            self.request,
            attachment.task,
        )

        return attachment



@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "note": {
                    "type": "string",
                    "description": "یادداشت مربوط به فایل‌ها",
                },
            },
            "required": ["files"],
        },
    },
    responses={
        201: InternalTaskAttachmentSerializer(
            many=True
        ),
    },
)
class InternalTaskCompleteView(
    generics.GenericAPIView
):

    serializer_class = (
        InternalTaskCompleteSerializer
    )

    permission_classes = [
        IsAuthenticated,
        InternalTaskModifyPermission,
    ]

    def get_queryset(self):

        return InternalTaskAccess.get_queryset(
            self.request.user
        )

    def post(self, request, pk):

        task = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        self.check_object_permissions(
            request,
            task,
        )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            task, archive = finalize_internal_task(
                task=task,
                final_action_by=request.user,
                status=InternalTask.Status.COMPLETED,
                attachment_files=(
                    serializer.validated_data.get(
                        "files",
                        [],
                    )
                ),
                attachment_note=(
                    serializer.validated_data.get(
                        "note",
                        "",
                    )
                ),
                uploaded_by=request.user,
            )

        except ValueError as exc:

            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            InternalTaskSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )



@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "note": {
                    "type": "string",
                    "description": "یادداشت مربوط به فایل‌ها",
                },
            },
            "required": ["files"],
        },
    },
    responses={
        201: InternalTaskAttachmentSerializer(
            many=True
        ),
    },
)
class InternalTaskCancelView(
    generics.GenericAPIView
):

    serializer_class = (
        InternalTaskCancelSerializer
    )

    permission_classes = [
        IsAuthenticated,
        InternalTaskModifyPermission,
    ]

    def get_queryset(self):

        return InternalTaskAccess.get_queryset(
            self.request.user
        )

    def post(self, request, pk):

        task = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        self.check_object_permissions(
            request,
            task,
        )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            task, archive = finalize_internal_task(
                task=task,
                final_action_by=request.user,
                status=InternalTask.Status.CANCELLED,
                attachment_files=(
                    serializer.validated_data.get(
                        "files",
                        [],
                    )
                ),
                attachment_note=(
                    serializer.validated_data.get(
                        "note",
                        "",
                    )
                ),
                uploaded_by=request.user,
            )

        except ValueError as exc:

            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            InternalTaskSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    request=None,
    responses={
        200: InternalTaskSerializer,
    },
)
class InternalTaskReopenView(
    generics.GenericAPIView
):

    serializer_class = InternalTaskReopenSerializer

    permission_classes = [
        IsAuthenticated,
        InternalTaskModifyPermission,
    ]

    def get_queryset(self):

        return InternalTaskAccess.get_queryset(
            self.request.user
        )

    def post(self, request, pk):

        task = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        self.check_object_permissions(
            request,
            task,
        )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            task = reopen_internal_task(
                task=task,
            )

        except ValueError as exc:

            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            InternalTaskSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )