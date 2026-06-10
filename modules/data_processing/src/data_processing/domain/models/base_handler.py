"""Base processing handler — implements Chain of Responsibility pattern."""

from abc import ABC, abstractmethod
from typing import Any

from building_block.core.domain.processing_step import ProcessingStep, ProcessingStepStatus

from data_processing.domain.models.processed_data import ProcessedData
from data_processing.services.adapters.audit_processing_result import (
    AuditProcessingResultAdapter,
)


class BaseProcessingHandler(ABC):
    """
    Abstract base class for all handlers in the processing chain.
    Implements Template Method and Chain of Responsibility patterns.
    """

    def __init__(self):
        self._next: "BaseProcessingHandler | None" = None
        self.audit_processing_result = AuditProcessingResultAdapter()

    def set_next(self, handler: "BaseProcessingHandler") -> "BaseProcessingHandler":
        """
        Set the next handler in the chain.
        Fluent interface — allows A.set_next(B).set_next(C).

        Args:
            handler: Next handler in the chain

        Returns:
            The handler passed in (for chaining)
        """
        self._next = handler
        return handler

    def handle(self, data: ProcessedData) -> ProcessedData:
        """
        Process data through this handler and pass to next.
        Template Method: orchestrates the chain.

        Args:
            data: Data to process

        Returns:
            Processed data (possibly modified by entire chain)
        """
        result = self._process(data)
        failed_step = self._get_failed_processing_step(result)
        if failed_step is not None:
            self.audit_processing_result.save(
                file_id=result.file_id,
                processing_step=data.processing_steps,
            )
            raise Exception(f"Processing step failed: {failed_step}")
        if self._next is not None:
            return self._next.handle(result)
        
        self.audit_processing_result.save(
                file_id=result.file_id,
                processing_step=data.processing_steps,
            )
        return result

    def _get_failed_processing_step(self, data: ProcessedData) -> dict[str, Any] | None:
        for processing_step in data.processing_steps:
            for step_name, step_result in processing_step.items():
                status = None
                error = None
                if isinstance(step_result, ProcessingStep):
                    status = step_result.status
                    error = step_result.error


                if status == ProcessingStepStatus.FAILED or status == "failed":
                    return {
                        "step_name": step_name,
                        "error": error,
                    }
        return None
    
        

    @abstractmethod
    def _process(self, data: ProcessedData) -> ProcessedData:
        """
        Business logic of this handler.
        Subclasses override this method.

        Args:
            data: Data to process

        Returns:
            Modified data for next handler
        """
        ...

    def __repr__(self) -> str:
        """String representation for debugging."""
        next_name = self._next.__class__.__name__ if self._next else "None"
        return f"{self.__class__.__name__} -> {next_name}"
