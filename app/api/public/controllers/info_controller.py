from sqlalchemy.ext.asyncio import AsyncSession

from app.api.public.schema.info_schema import InitialInfoResponseSchema
from app.api.public.services.info_service import InfoService, get_info_service


class InfoController:
    def __init__(self, service: InfoService):
        self.service = service

    async def initialize_info_controller(
        self, db: AsyncSession
    ) -> InitialInfoResponseSchema:
        response = await self.service.initialize_info(db=db)
        return response


def get_info_controller() -> InfoController:
    return InfoController(service=get_info_service())
