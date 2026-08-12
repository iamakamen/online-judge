from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class TestCaseCreate(BaseModel):
    input: str
    expected_output: str
    run_enabled: bool = False
    submit_enabled: bool = False
    is_sample: bool = False
    display_order: int

    @model_validator(mode="after")
    def has_execution_purpose(self):
        if not self.run_enabled and not self.submit_enabled:
            raise ValueError(
                "Test case must be enabled for run or submit"
            )
        return self


class TestCaseUpdate(BaseModel):
    input: str | None = None
    expected_output: str | None = None
    run_enabled: bool | None = None
    submit_enabled: bool | None = None
    is_sample: bool | None = None
    display_order: int | None = None

    @model_validator(mode="after")
    def has_execution_purpose(self):
        if (
            self.run_enabled is not None
            and self.submit_enabled is not None
            and not self.run_enabled
            and not self.submit_enabled
        ):
            raise ValueError(
                "Test case must be enabled for run or submit"
            )
        return self


class PublicTestCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    input: str
    expected_output: str
    is_sample: bool
    display_order: int
