from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import get_object_or_404
from PIL import Image
import face_recognition
import pandas as pd
import numpy as np
import cv2,os
from django.conf import settings
from sortedcontainers import SortedSet
from pathlib import Path
from database.models import Student,Faculty,Degree,Course
BASE_DIR = Path(__file__).resolve().parent.parent

def get_encodings(images):
    face_encodings = []
    for image in images:
        loaded_image = face_recognition.load_image_file(image)
        encoding = face_recognition.face_encodings(loaded_image)
        if encoding:
            face_encodings.append(encoding[0])
    return face_encodings

def login(request):
    if request.method=="POST":
        is_faculty = request.POST.get("isfaculty")
        name = request.POST.get("name")
        pass1 = request.POST.get("password")
        if is_faculty is None:
            student = Student.objects.get(name=name)
            if student.password != pass1:
                return HttpResponse("Invalid Username or Password")
            # user = authenticate(request, username=name, password=pass1)
            # auth_login(request, user)
            return redirect(f'/{name}/0/')
        else:
            faculty = Faculty.objects.get(username = name)
            if faculty.password != pass1:
                return HttpResponse("Invalid Username or Password")
            # user = authenticate(request, username=name, password=pass1)
            # auth_login(request, user)
            return redirect(f'/{name}/1/')
    return render(request,'login.html')

def selectdegree(request,name,isface):
    return render(request,'selectdegree.html')

def selectyear(request,name,isface,degree):
    degree = Degree.objects.get(degree=degree)
    years = degree.years
    years = np.array(list(map(int, years.split("_"))))
    return render(request,'selectyear.html',{'years':years})

def selectbranch(request,name,isface,degree,year):
    degree = Degree.objects.get(degree=degree)
    branches = degree.branches
    branches = np.array(branches.split('_'))
    return render(request,'selectbranch.html',{'branches':branches})

def selectcourse(request,name,isface,degree,year,branch):
    courses = Course.objects.filter(degree__contains=degree, year__contains=year, branch__contains=branch)
    isface = int(isface)
    return render(request,'selectcourse.html',{'courses':courses, 'isfac':isface,'name':name})

def signup(request):    
    return render(request,'signup.html')

def faculty_signup(request):
    if request.method=="POST":
        name = request.POST.get('name')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        pass2 = request.POST.get('pass2')
        key = request.POST.get('key')
        if key!="IITINDORE":
            return HttpResponse("Please enter correct Secret Key")
        if(pass1!=pass2):
            return HttpResponse("Please enter same password!")
        faculty = Faculty(username=name,password=pass1) 
        faculty.save()
        return redirect('/')
    return render(request,'faculty_signup.html')

def student_signup(request):
    if request.method=="POST":
        name = request.POST.get('name')
        roll_no= request.POST.get('roll_no')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        image = request.FILES.getlist('image')
        if(pass1!=pass2):
            return HttpResponse("Please enter same password!")
        encodings = get_encodings(image)
        print(encodings)
        student = Student(name=name,roll_no=roll_no,password=pass1,Encodings=encodings) 
        student.save()
        return redirect('/')
    return render(request,'student_signup.html')

def logout(request):
    # auth_logout(request)
    return redirect('/')

def home(request,name,isface,degree,year,branch,course):
    if request.method=="POST":
        images = request.FILES.getlist('image')
        date = request.POST.get("date")
        attendance = SortedSet()
        req_course = get_object_or_404(Course, course=course, year=year, branch=branch, degree=degree)
        students_in_course = req_course.student.all()
        encodings = np.array([student.Encodings for student in students_in_course])
        actual_encodings = []
        for encoding in encodings:
            encoding = encoding[8:-3]
            encoding = encoding.replace('\n', '').replace(' ', '')
            numpy_array = np.array([float(value) for value in encoding[1:-1].split(',')])
            actual_encodings.append(numpy_array)
        roll_no = np.array([student.roll_no for student in students_in_course])
        for image in images:
            gp_pic = face_recognition.load_image_file(image)
            face_locations = face_recognition.face_locations(gp_pic, number_of_times_to_upsample=2)
            face_encodings = face_recognition.face_encodings(gp_pic, face_locations)

            j=0
            for face_location in face_locations:
                top, right, bottom, left = face_location
                face_image = gp_pic[top:bottom, left:right]
                sharpened = cv2.addWeighted(face_image, 2, cv2.GaussianBlur(face_image, (0, 0), 30), -1, 0)
                blurred = cv2.GaussianBlur(sharpened, (5, 5), 0)
                kernel = np.ones((5, 5), np.float32) / 25
                face_image = cv2.filter2D(blurred, -1, kernel)
                curr_check =  face_encodings[j]
                j = j+1
                ind=0
                check=100
                for i in range(len(actual_encodings)):
                
                    results = face_recognition.face_distance([curr_check], actual_encodings[i])

                    if(check>results):
                        check = min(check,results)
                        ind=i
                if check<0.6:
                    attendance.add(roll_no[ind])
        print(attendance)
        attendance = [1 if roll in attendance else 0 for roll in roll_no]
        today_attendance = np.array(attendance)
        data = {'roll_no':roll_no}
        data = pd.DataFrame(data)
        zipped_data = zip(roll_no, attendance)
        context = {'zipped_data': zipped_data,'course': course,'isfac':isface,'year':year,'degree':degree,'branch':branch, 'name':name}
        data[date] = today_attendance
        output_csv_file = os.path.join(settings.STATIC_ROOT, 'output_data.csv')
        data.to_csv(output_csv_file, index=False)
        return render(request,'viewattendance.html',context)
    return render(request,'home.html',{'isfac':isface,'year':year,'degree':degree,'branch':branch,'course':course,'name':name})

def attendance(request,name,isface,degree,year,branch,course):
    if request.method=="POST":
        images = request.FILES.getlist('image')
        date = request.POST.get("date")
        attendance = SortedSet()
        data = pd.read_csv("static\_features_3.csv")
        ref_face_encodings = data.iloc[:,:-1].values
        name = data.iloc[:,-1].values
        # print(images)
        for image in images:
            gp_pic = face_recognition.load_image_file(image)
            face_locations = face_recognition.face_locations(gp_pic, number_of_times_to_upsample=2)
            face_encodings = face_recognition.face_encodings(gp_pic, face_locations)

            # print("I found {} face(s) in this photograph.".format(len(face_locations)))
            j=0
            for face_location in face_locations:
                top, right, bottom, left = face_location
                face_image = gp_pic[top:bottom, left:right]
                sharpened = cv2.addWeighted(face_image, 2, cv2.GaussianBlur(face_image, (0, 0), 30), -1, 0)
                blurred = cv2.GaussianBlur(sharpened, (5, 5), 0)
                kernel = np.ones((5, 5), np.float32) / 25
                face_image = cv2.filter2D(blurred, -1, kernel)
                # print(face_image)
                # pil_image = Image.fromarray(face_image)
                # display(pil_image)
                curr_check =  face_encodings[j]
                j = j+1
                ind=0
                check=100
                for i in range(len(ref_face_encodings)):
                
                    results = face_recognition.face_distance([curr_check], ref_face_encodings[i])

                    if(check>results):
                        check = min(check,results)
                        ind=i

                # print(name[ind].split('-')[0],"is present..")
                # print("__________________________________________")
                attendance.add(name[ind].split('_')[0])

        roll_no = ['220001001', '220001002', '220001003', '220001004', '220001005', '220001006', '220001007', '220001008', '220001009', '220001010', '220001011', '220001012', '220001013', '220001014', '220001015', '220001016', '220001017', '220001018', '220001019', '220001020', '220001021', '220001022', '220001023', '220001024', '220001025', '220001026', '220001027', '220001028', '220001029', '220001031', '220001032', '220001033', '220001034', '220001035', '220001036', '220001037', '220001038', '220001039', '220001040', '220001041', '220001042', '220001043', '220001044', '220001045', '220001046', '220001047', '220001048', '220001049', '220001050', '220001051', '220001052', '220001053', '220001054', '220001055', '220001056', '220001057', '220001058', '220001059', '220001060', '220001061', '220001062', '220001063', '220001064', '220001065', '220001066', '220001067', '220001068', '220001069', '220001070', '220001071', '220001073', '220001074', '220001075', '220001076', '220001077', '220001078', '220001079', '220001080', '220001081', '220001082', '220002018', '220002029', '220002063', '220002081']

        data = pd.read_csv('static\output_data.csv')

        attendance = [1 if roll in attendance else 0 for roll in roll_no]
        roll_no = np.array(roll_no)
        today_attendance = np.array(attendance)
        zipped_data = zip(roll_no, attendance)
        context = {'zipped_data': zipped_data,'isfac':isface,'year':year,'degree':degree,'branch':branch}
        data[date] = today_attendance
        output_csv_file = os.path.join(settings.STATIC_ROOT, 'output_data.csv')

        data.to_csv('static\output_data.csv', index=False)
        # no = len(roll_no)
        return render(request,'viewattendance.html',context)
    return render(request,'home.html',{'isfac':isface,'year':year,'degree':degree,'branch':branch})

def enroll(request,name,isface,degree,year,branch,course):
    print(name)
    student = Student.objects.get(name=name)
    course = Course.objects.get(course=course)
    course.student.add(student)
    course.save()
    return HttpResponse("Successfully enrolled into the course!")

def viewattendance(request,name,isface,degree,year,branch,course):
    if request.method =="POST":
        file = os.path.join(settings.STATIC_ROOT, 'output_data.csv')
        response = HttpResponse(open(file, 'rb').read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{file}"'
        return response
    return render(request,'viewattendance.html',{'isfac':isface,'year':year,'degree':degree,'branch':branch,'course':course})