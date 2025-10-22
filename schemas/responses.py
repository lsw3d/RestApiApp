from pydantic import BaseModel


class PhoneNumberOut(BaseModel):
    id: int
    number: str

    model_config = {"from_attributes": True}


class BuildingOut(BaseModel):
    id: int
    address: str

    model_config = {"from_attributes": True}


class ActivityOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class OrganizationOut(BaseModel):
    id: int
    name: str
    building: BuildingOut
    phone_numbers: list[PhoneNumberOut]
    activities: list[ActivityOut]

    model_config = {"from_attributes": True}


class Response(BaseModel):
    result: bool


class SuccessResponse(Response):
    result: bool = True
    data: OrganizationOut | list[OrganizationOut] | None


class ErrorResponse(Response):
    result: bool = False
    detail: str | None = None
