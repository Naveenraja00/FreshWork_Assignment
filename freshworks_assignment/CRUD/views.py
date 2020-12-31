import sys,time,os,json
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.contrib import messages
class details:
    data={}
    def __init__(self):
        with open("userdetails\\userrecords.json","r") as f:
            self.data=json.load(f)
    def reggi(self,data):
        try:
            os.mkdir("userdetails")
        except FileExistsError as e:
            pass
        with open("userdetails\\userrecords.json","w") as f:
            json.dump(data,f,indent=3)
user=None
auth=None
def register(request):
    if request.method=="POST":
        username = request.POST["username"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        email = request.POST["email"]
        password = request.POST["password"]
        repass = request.POST["conform_pass"]
        obj = details()
        if username in obj.data:
            messages.info(request, "Username taken...")
            return redirect("/")
        elif password != repass:
            messages.info(request, "password mismatch")
            return redirect("/")
        else:
            new = {"username": username, "firstname": firstname, "lastname": lastname, "email": email,
                   "password": password}
            obj.data[username] = new
            obj.reggi(obj.data)
            messages.info(request, "Registerd successfully")
            return redirect("/")
    else:
        return render(request,"register.html")

def loginverify(request):
    global user, auth
    user=None
    user=details()
    if (request.method=="POST"):
        username = request.POST["username"]
        password = request.POST["password"]
        auth = {}
        try:
            check = auth[username]
        except Exception as e:
            try:
                check = user.data[username]
            except KeyError as er:
                messages.info(request, "INVALID CREDENTIAL")
                auth = None
                return redirect("/")
            else:
                if user.data[username]["password"] == password:
                    auth[username] = "is_active"
                else:
                    messages.info(request, "INVALID CREDENTIAL")
                    auth = None
                    return redirect("/")
        return redirect("home")
    else:
        return render(request, "index.html")

def home(request):
    global auth
    if auth!=None:
        return render(request,"home.html")
    else:
        return redirect("/")

def crud(request):
    global auth
    if auth != None:
        op = request.POST["op"]
        if op == "1":
            return redirect("create")
        elif op == "2":
            return redirect("write")
        elif op == "3":
            return redirect("read")
        elif op == "4":
            return redirect("delete")
        elif op == "5":
            auth = None
            return redirect("/")
        else:
            messages.info(request, "Invalid Operation ")
            return redirect("home")
    else:
        return redirect("/")

def create(request):
    global auth
    if auth != None:
        if request.method=="POST":
            filepath = request.POST["filepath"]
            filename = request.POST["filename"]
            if filepath != ".":
                filename = filepath + filename
            else:
                filename = "datastore/" + filename
            if not os.path.exists(filename):
                try:
                    with open(filename, "x") as f:
                        pass
                except PermissionError as e:
                    messages.info(request, f"Permission denied on {filepath} path")
                    return redirect("home")
                except FileNotFoundError as e:
                    messages.info(request, "Enter valid path.....(end with '/')")
                    return redirect("home")
            check = request.POST["check"]
            if (check == "yes") or (check == "YES"):
                return redirect("write")
            else:
                messages.info(request, f"{filename} created ")
                return redirect("home")
        else:
            return render(request,"create.html")
    else:
        return redirect("/")

def write(request):
    global auth
    if auth != None:
        if request.method == "POST":
            filename = request.POST["filename"]
            if os.path.exists(filename):
                key = request.POST["key"]
                data = None
                try:
                    with open(filename, "r") as f:
                        data = json.load(f)
                except Exception as e:
                    pass
                else:
                    if key in data:
                        if data[key]["exp"] > time.time():
                            messages.info(request, f"Key=>{key} already taken")
                            return ("home")
                keytime = int(request.POST["time"])
                reg = request.POST["reg"]
                dob = request.POST["dob"]
                branch = request.POST["branch"]
                email = request.POST["email"]
                mob = request.POST["mob"]
                newdata = {"register": reg, "name": key, "DOB(mm-dd-yyyy)": dob, "branch": branch, "email": email,
                           "mob": mob}
                if keytime == 0:
                    newdata["exp"] = keytime
                else:
                    newdata["exp"] = time.time() + keytime
                if sys.getsizeof(newdata) > 16000:
                    messages.info(request, f"You enter more than 16 kb for {key},data not accept")
                    return redirect("home")
                if data == None:
                    data = {}
                data[key] = newdata
                with open(filename, "w") as f:
                    json.dump(data, f, indent=3)
                messages.info(request, f"written successfully on {filename}")
                return redirect("home")
            else:
                messages.info(request, f"requested file({filename}) for write not found")
                return redirect("home")
        else:
            return render(request,"write.html")
    else:
        return redirect("/")

def read(request):
    global auth
    if auth != None:
        if request.method=="POST":
            c = 0
            filename = request.POST["filename"]
            if os.path.exists(filename):
                key = request.POST["key"]
                key = list(map(str, key.strip().split(",")))
                data = None
                try:
                    with open(filename, "r") as f:
                        data = json.load(f)
                except Exception as e:
                    messages.info(request, f"{filename} is empty file")
                    return redirect("home")
                if key[0] == "_all":
                    found = []
                    for i in data:
                        if data[i]["exp"] != 0:
                            if data[i]["exp"] <= time.time():
                                found.append(i)
                                c = 1
                    for i in found:
                        del data[i]
                    if c:
                        with open(filename, "w") as f:
                            json.dump(data, f, indent=3)
                    if sys.getsizeof(data) <= 16000:
                        return JsonResponse(data, safe=False)
                    else:
                        messages.info(request, f"requested key=>{key} for read size exceeds 16 kb")
                        return redirect("home")
                else:
                    notfound = []
                    newdata = {}
                    for i in key:
                        try:
                            check = data[i]
                        except KeyError as e:
                            notfound.append(i)
                        else:
                            if data[i]["exp"] != 0:
                                if data[i]["exp"] <= time.time():
                                    del data[i]
                                    notfound.append(i)
                                    c = 1
                                else:
                                    newdata[i] = data[i]
                            else:
                                newdata[i] = data[i]
                    else:
                        newdata["notfound keys"] = notfound
                    if c:
                        with open(filename, "w") as f:
                            json.dump(data, f, indent=3)
                    if sys.getsizeof(newdata) <= 16000:
                        return JsonResponse(newdata, safe=False)
                    else:
                        messages.info(request, f"requested key=>{filename} for read size exceeds 16 kb")
                        return redirect("home")

            else:
                messages.info(request, f"requested file({filename})  not found")
                return redirect("home")
        else:
            return render(request,"read.html")
    else:
        return redirect("/")

def delete(request):
    global auth
    if auth != None:
        if request.method=="POST":
            filename = request.POST["filename"]
            if os.path.exists(filename):
                key = request.POST["key"]
                key = list(map(str, key.strip().split(",")))
                data = None
                try:
                    with open(filename, "r") as f:
                        data = json.load(f)
                except Exception as e:
                    messages.info(request, f"{filename} is  Already empty file")
                    return redirect("home")
                if key[0] == "_all":
                    with open(filename, "w") as f:
                        pass
                    messages.info(request, f"{key} deleted successfully")
                    return redirect("home")
                else:
                    notfound = []
                    for i in key:
                        try:
                            check = data[i]
                        except KeyError as e:
                            notfound.append(i)
                        else:
                            if data[i]["exp"] != 0:
                                if data[i]["exp"] <= time.time():
                                    del data[i]
                                    notfound.append(i)
                            else:
                                del data[i]
                    else:
                        with open(filename, "w") as f:
                            json.dump(data, f, indent=3)
                        data = {}
                        data["notfound keys"] = notfound
                        return JsonResponse(data, safe=False)
            else:
                messages.info(request, f"requested file({filename}) not found")
                return redirect("home")
        else:
            return render(request,"delete.html")
    else:
        return redirect("/")