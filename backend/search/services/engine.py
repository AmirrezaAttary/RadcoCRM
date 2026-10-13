from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchResult:
    type: str
    id: int
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    score: float
    url: str

    def to_dict(self):
        return {
            "type": self.type,
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "score": round(float(self.score), 4),
            "url": self.url,
        }


class SearchEngine:

    MAX_RESULTS = 20
    LIMIT_PER_PROVIDER = 5

    URLS = {
        "employee": "/accounts/api/v1/employee/{id}/",

        "customer": "/customers/api/v1/customers/{id}/",

        "department": "/department/api/v1/department/{id}/",
        "department_step": "/department/api/v1/department_step/{id}/",

        "case": "/tasks/api/v1/cases/{id}/",
        "task": "/tasks/api/v1/tasks/{id}/",
        "internal_task": "/tasks/api/v1/internal-tasks/{id}/",
        "resource": "/tasks/api/v1/cases/resources/{id}/",
        "task_attachment": "/tasks/api/v1/tasks/attachments/{id}/",
        "internal_task_attachment": "/tasks/api/v1/internal-task/{id}/attachments/",
        "task_step_log": "/tasks/api/v1/tasks/{id}/logs/",

        "score": "/score/api/v1/employee/{id}/history",

        "purchase_task": "/purchasing/api/v1/tasks/{id}/",
        "purchase_process_step": "/purchasing/api/v1/steps/{id}/",
        "purchase_task_attachment": "/purchasing/api/v1/task-attachments/{id}/",

        "quality_control": "/quality_control/api/v1/{id}/",
        "quality_control_employee": "/quality_ontrol/api/v1/employee/{id}/",

        "product": "/warehouse/api/v1/products/{id}/",
        "product_category": "/warehouse/api/v1/products/categories/{id}/",

        "order_task": "/warehouse/api/v1/order_task/{id}/",
        "order_task_deadline": "/warehouse/api/v1/order_task/deadlines/{id}/",
        "order_task_attachment": "/warehouse/api/v1/order_task/attachment/{id}/",

        "inventory_stock": "/warehouse/api/v1/process/stock/{id}/",
        "stock_transaction": "/warehouse/api/v1/process/transactions/{id}/",
        "warehouse_staff": "/warehouse/api/v1/staff/{id}/",
        "warehouse_task": "/warehouse/api/v1/task/{id}/",
    }

    @classmethod
    def url(cls, result_type, object_id):
        return cls.URLS[result_type].format(id=object_id)

    @classmethod
    def result(
        cls,
        *,
        result_type,
        object_id,
        title,
        subtitle=None,
        description=None,
        score=0,
    ):
        return SearchResult(
            type=result_type,
            id=object_id,
            title=title,
            subtitle=subtitle,
            description=description,
            score=score,
            url=cls.url(result_type, object_id),
        )

    @classmethod
    def search(cls, query, user=None):
        from .normalizer import SearchNormalizer

        from .providers.employee import EmployeeProvider
        from .providers.customer import CustomerProvider
        from .providers.department import DepartmentProvider
        from .providers.department_step import DepartmentStepProvider
        from .providers.case import CaseProvider
        from .providers.task import TaskProvider
        from .providers.internal_task import InternalTaskProvider
        from .providers.resource import ResourceProvider
        from .providers.task_attachment import TaskAttachmentProvider
        from .providers.internal_task_attachment import (
            InternalTaskAttachmentProvider,
        )
        from .providers.score import ScoreProvider
        from .providers.task_step_log import TaskStepLogProvider
        from .providers.purchase_task import PurchaseTaskProvider
        from .providers.purchase_process_step import PurchaseProcessStepProvider
        from .providers.purchase_task_attachment import (
            PurchaseTaskAttachmentProvider,
        )
        from .providers.quality_control import QualityControlProvider
        from .providers.quality_control_employee import (
            QualityControlEmployeeProvider,
        )
        from .providers.product import ProductProvider
        from .providers.product_category import ProductCategoryProvider
        from .providers.order_task import OrderTaskProvider
        from .providers.order_task_deadline import OrderTaskDeadlineProvider
        from .providers.order_task_attachment import OrderTaskAttachmentProvider
        from .providers.inventory_stock import InventoryStockProvider
        from .providers.stock_transaction import StockTransactionProvider
        from .providers.warehouse_staff import WarehouseStaffProvider
        from .providers.warehouse_task import WarehouseTaskProvider

        query = SearchNormalizer.normalize(query)

        if not query:
            return []

        providers = [
            EmployeeProvider,
            CustomerProvider,
            DepartmentProvider,
            DepartmentStepProvider,
            CaseProvider,
            TaskProvider,
            InternalTaskProvider,
            ResourceProvider,
            TaskAttachmentProvider,
            InternalTaskAttachmentProvider,
            ScoreProvider,
            TaskStepLogProvider,
            PurchaseTaskProvider,
            PurchaseProcessStepProvider,
            PurchaseTaskAttachmentProvider,
            QualityControlProvider,
            QualityControlEmployeeProvider,
            ProductProvider,
            ProductCategoryProvider,
            OrderTaskProvider,
            OrderTaskDeadlineProvider,
            OrderTaskAttachmentProvider,
            InventoryStockProvider,
            StockTransactionProvider,
            WarehouseStaffProvider,
            WarehouseTaskProvider,
        ]

        results = []

        for provider in providers:
            provider_results = provider.search(
                query=query,
                user=user,
                limit=cls.LIMIT_PER_PROVIDER,
            )

            results.extend(provider_results)

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return [
            result.to_dict()
            for result in results[:cls.MAX_RESULTS]
        ]