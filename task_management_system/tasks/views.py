from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm
from django.contrib.auth.models import User
from firebase_admin import db
from datetime import datetime

# Hàm lưu hoặc cập nhật dữ liệu vào Firebase Realtime Database
def save_or_update_task_in_firebase(task_key, task_data):
    ref = db.reference(f'tasks/{task_key}')  
    ref.set(task_data)

# Hàm lấy dữ liệu từ Firebase Realtime Database
def get_tasks_from_firebase():
    ref = db.reference('tasks')  
    tasks = ref.get()  
    return tasks

# View tạo task mới
@login_required(login_url='tasks:login')
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # Chuyển đổi đối tượng date sang chuỗi để lưu vào Firebase
            deadline_str = form.cleaned_data['deadline'].strftime('%Y-%m-%d')
            task_data = {
                'title': form.cleaned_data['title'],
                'description': form.cleaned_data['description'],
                'priority': form.cleaned_data['priority'],
                'deadline': deadline_str,
                'completed': form.cleaned_data['completed'],
                'user': request.user.username 
            }
            # Tạo task mới
            save_or_update_task_in_firebase(None, task_data)
            return redirect('tasks:list')
    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form})

# View đăng nhập
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tasks:list')
        else:
            return render(request, 'login.html', {'error': 'Thông tin đăng nhập không hợp lệ'})
    return render(request, 'login.html')

# View đăng xuất
def logout_view(request):
    logout(request)
    return redirect('tasks:login')

# View đăng ký người dùng mới
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password != password_confirm:
            return render(request, 'register.html', {'error': 'Mật khẩu không khớp'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Tên đăng nhập đã tồn tại'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email đã được sử dụng'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect('tasks:login')
    return render(request, 'register.html')

# View danh sách công việc
@login_required(login_url='tasks:login')
def task_list(request):
    tasks = get_tasks_from_firebase()
    
    # Thêm logic đếm ngược tới deadline cho mỗi công việc
    task_list = []
    for task_key, task_value in tasks.items():
        # Kiểm tra xem task_value có phải là dictionary không
        if isinstance(task_value, dict):
            deadline = task_value.get('deadline')
            if deadline:
                deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
                remaining_days = (deadline - datetime.now().date()).days
            else:
                remaining_days = None
            task_list.append({
                'key': task_key,
                'title': task_value.get('title', 'No Title'),
                'description': task_value.get('description', ''),
                'priority': task_value.get('priority', 'low'),
                'deadline': deadline,
                'completed': task_value.get('completed', False),
                'remaining_days': remaining_days
            })
    
    return render(request, 'task_list.html', {'tasks': task_list})

# View chỉnh sửa công việc
@login_required(login_url='tasks:login')
def edit_task(request, task_id):
    tasks = get_tasks_from_firebase()
    task = tasks.get(task_id)
    
    if task is None:
        return redirect('tasks:list')

    if request.method == 'POST':
        form = TaskForm(request.POST, initial=task)
        if form.is_valid():
            # Chuyển đổi đối tượng date sang chuỗi
            deadline_str = form.cleaned_data['deadline'].strftime('%Y-%m-%d')
            task_data = {
                'title': form.cleaned_data['title'],
                'description': form.cleaned_data['description'],
                'priority': form.cleaned_data['priority'],
                'deadline': deadline_str,
                'completed': form.cleaned_data['completed'],
                'user': request.user.username
            }
            # Cập nhật task cũ
            save_or_update_task_in_firebase(task_id, task_data)
            return redirect('tasks:list')
    else:
        form = TaskForm(initial=task)
    return render(request, 'edit_task.html', {'form': form, 'task': task})

# View xóa công việc
@login_required(login_url='tasks:login')
def delete_task(request, task_id):
    tasks = get_tasks_from_firebase()
    task = tasks.get(task_id)
    
    if task is None:
        return redirect('tasks:list')

    ref = db.reference(f'tasks/{task_id}')
    ref.delete()
    return redirect('tasks:list')
