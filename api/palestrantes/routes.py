from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from typing import List
from .database import get_db
from .models import Palestrante, PalestranteCreate, PalestranteDB
import re


route = APIRouter()

def verificar_cpf(cpf: str) -> bool:
	match_digits = re.match("\d{11}", cpf)
	
	if len(cpf) == 11 and match_digits:
		return True
	
	return False

@route.post(
	"/", 
	response_model=Palestrante, 
	tags=["palestrantes"],
)
def criar_palestrante(palestrante: PalestranteCreate, db: Session = Depends(get_db)):
	if not verificar_cpf(palestrante.cpf):
		raise HTTPException(status_code=400, detail="O CPF informado é inválido. O formato aceito é composto somente por números.")
	db_palestrante = db.query(PalestranteDB).filter(PalestranteDB.cpf == palestrante.cpf).first()
	if db_palestrante:
		raise HTTPException(status_code=400, detail="CPF já cadastrado")

	novo_palestrante = PalestranteDB(nome=palestrante.nome, assunto=palestrante.assunto, cpf=palestrante.cpf)
	db.add(novo_palestrante)
	db.commit()
	db.refresh(novo_palestrante)
	return novo_palestrante

@route.get(
	"/",
	response_model=List[Palestrante],
	tags=["palestrantes"]	
)
def listar_palestrantes(db: Session = Depends(get_db)):
	palestrantres = db.query(PalestranteDB).all()
	return palestrantres

@route.get(
	"/{palestrante_cpf}",
	response_model=Palestrante,
	tags=["palestrantes"]	
)
def obter_palestrante_cpf(cpf: str, db: Session = Depends(get_db)):
	if not verificar_cpf(cpf):
		raise HTTPException(status_code=400, detail="O CPF informado é inválido. O formato aceito é composto somente por números.")
	db_palestrante = db.query(PalestranteDB).filter(PalestranteDB.cpf == cpf).first()
	if db_palestrante is None:
		raise HTTPException(status_code=404, detail="Palestrante não encontrado")
	return db_palestrante

@route.delete(
	"/{palestrante_cpf}", 
	tags=["palestrantes"],
)
def deletar_palestrante(
	cpf: str = Path(..., title="O cpf do palestrante a ser deletado"),
	db: Session = Depends(get_db),
):
	if not verificar_cpf(cpf):
		raise HTTPException(status_code=400, detail="O CPF informado é inválido. O formato aceito é composto somente por números.")
	palestrante = db.query(PalestranteDB).filter(PalestranteDB.cpf == cpf).first()
	if palestrante is None:
			raise HTTPException(status_code=404, detail="Palestrante não encontrado")
	db.delete(palestrante)
	db.commit()
	return {"mensagem": "Palestrante deletado com sucesso"}