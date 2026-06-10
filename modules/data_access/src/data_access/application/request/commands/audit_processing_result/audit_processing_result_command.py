from building_block.core.domain.processing_step import ProcessingStep

from ..base_command import Command


class AuditProccessingResultCommand(Command):
    file_id:str
    proccessing_step:list[dict[str, ProcessingStep]]
