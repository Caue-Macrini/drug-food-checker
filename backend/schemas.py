from typing import Literal
from pydantic import BaseModel, Field, field_validator
import re

class Login(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=72)
    @field_validator('email')
    @classmethod
    def email_valid(cls, value):
        value = value.strip().lower()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
            raise ValueError('E-mail inválido')
        return value
    @field_validator('password')
    @classmethod
    def bytes_valid(cls, value):
        if len(value.encode()) > 72:
            raise ValueError('Senha deve ter até 72 bytes UTF-8')
        return value

class Signup(Login):
    name: str = Field(min_length=2, max_length=120)
    consent: Literal[True]
    @field_validator('password')
    @classmethod
    def strong(cls, value):
        if len(value) < 10:
            raise ValueError('Use pelo menos 10 caracteres')
        return value

class Supplement(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    dosage: str = Field(default='', max_length=100)
    frequency: str = Field(default='', max_length=100)

class ClinicalProfile(BaseModel):
    age: int | None = Field(default=None, ge=0, le=120)
    weight: float | None = Field(default=None, ge=1, le=500)
    height: float | None = Field(default=None, ge=30, le=250)
    conditions: list[str] = Field(default_factory=list, max_length=30)
    supplements: list[Supplement] = Field(default_factory=list, max_length=30)
    medications: list[str] = Field(default_factory=list, max_length=50)
    alcohol_frequency: int = Field(default=0, ge=0, le=7)
    renal_stage: int = Field(default=0, ge=0, le=5)
    hepatic_insufficiency: bool = False
    @field_validator('conditions', 'medications')
    @classmethod
    def list_limits(cls, value):
        if any(len(x) > 120 for x in value):
            raise ValueError('Cada item deve ter até 120 caracteres')
        return list(dict.fromkeys(x.strip() for x in value if x.strip()))

class Check(BaseModel):
    drug_id: str = Field(max_length=36)
    food_id: str = Field(max_length=36)
    personalize: bool = True

class EmailRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)

class ResetRequest(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    password: str = Field(min_length=10, max_length=72)
    @field_validator('password')
    @classmethod
    def valid_password(cls, value):
        return Login.bytes_valid(value)

class PasswordRequest(BaseModel):
    password: str = Field(min_length=1, max_length=72)

class AccountAction(BaseModel):
    active: bool

class ImportRow(BaseModel):
    source_record_id: str = Field(default='', max_length=100)
    source_text_id: str = Field(default='', max_length=100)
    evidence_status: str = Field(default='Associação documentada; classificação não validada', max_length=255)
    drug: str = Field(min_length=1, max_length=255)
    food: str = Field(min_length=1, max_length=255)
    drug_aliases: list[str] = Field(default_factory=list, max_length=30)
    food_aliases: list[str] = Field(default_factory=list, max_length=30)
    base_risk: int | None = Field(default=None, ge=0, le=2)
    risk_basis: str = Field(default='', max_length=1000)
    reviewed: bool = False
    mechanism: str = Field(min_length=1, max_length=4000)
    explanation: str = Field(min_length=1, max_length=4000)
    compound: str = Field(default='Não especificado na fonte', max_length=255)
    interaction_type: str = Field(default='Não classificada', max_length=100)
    reference_title: str = Field(min_length=1, max_length=500)
    reference_url: str = Field(max_length=1500)
    cyp450: bool = False
    renal_excretion: bool = False
    hepatotoxic: bool = False
    @field_validator('reference_url')
    @classmethod
    def safe_url(cls, value):
        if not value.startswith('https://'):
            raise ValueError('A referência deve usar HTTPS')
        return value

class ImportDataset(BaseModel):
    version: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=500)
    rows: list[ImportRow] = Field(min_length=1, max_length=10000)
