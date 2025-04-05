from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.public.schema.info_schema import IndustryResponseSchema
from app.modules.public.services.info_service import InfoService


class InfoController:
    def __init__(self, service: InfoService = Depends(InfoService)):
        self.service = service

    async def initialize_info_controller(
        self, db: AsyncSession
    ) -> List[IndustryResponseSchema]:
        response = await self.service.initialize_info(db=db)
        return response

    async def get_all_industries_controller(
        self, db: AsyncSession
    ) -> List[IndustryResponseSchema]:
        response = await self.service.get_all_industries(db=db)
        return response
