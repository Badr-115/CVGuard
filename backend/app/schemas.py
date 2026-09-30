from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    organization_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

    @field_validator("organization_name")
    @classmethod
    def clean_org(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Organization name is required")
        return value


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=10, max_length=10000)
    required_skills: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("title", "description")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty")
        return value

    @field_validator("required_skills")
    @classmethod
    def clean_skills(cls, value: list[str]) -> list[str]:
        result = []
        seen = set()
        for skill in value:
            skill = " ".join(skill.split()).strip()
            if skill and skill.casefold() not in seen:
                result.append(skill[:100])
                seen.add(skill.casefold())
        return result


class JobOut(BaseModel):
    id: int
    title: str
    description: str
    required_skills: list[str]
    score: float | None = None


class CandidateOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    score: float | None
    resume_uploaded: bool


class CandidateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    phone: str = Field(default="", max_length=80)
