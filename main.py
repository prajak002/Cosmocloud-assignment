from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
client = MongoClient("mongodb+srv://prajaksens:LBYiVZjb0XO9MpoX@cluster0.3lkbd1w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["library_database"]
students_collection = db["students"]

# Define Pydantic models
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

# FastAPI instance
app = FastAPI()

# Create Student
@app.post("/students/", status_code=201)
async def create_student(student: Student):
    student_dict = student.dict()
    result = students_collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}

# List Students
@app.get("/students/", status_code=200)
async def list_students(country: str = Query(None), age: int = Query(None)):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}

    students = list(students_collection.find(query, {"_id": 0}))
    return {"data": students}

# Fetch Student
@app.get("/students/{student_id}", status_code=200)
async def get_student(student_id: str):
    student = students_collection.find_one({"_id": ObjectId(student_id)}, {"_id": 0})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Update Student
@app.patch("/students/{student_id}", status_code=204)
async def update_student(student_id: str, student: Student):
    student_dict = student.dict()
    result = students_collection.update_one({"_id": ObjectId(student_id)}, {"$set": student_dict})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

# Delete Student
@app.delete("/students/{student_id}", status_code=200)
async def delete_student(student_id: str):
    result = students_collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

# Add dummy data
dummy_students = [
    {"name": "John Doe", "age": 25, "address": {"city": "New York", "country": "USA"}},
    {"name": "Jane Smith", "age": 22, "address": {"city": "London", "country": "UK"}},
    {"name": "Alice Johnson", "age": 30, "address": {"city": "Paris", "country": "France"}},
]

for student in dummy_students:
    students_collection.insert_one(student)
