from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone



class User(AbstractUser):
    # Add a new field to the user model
    student_id = models.CharField(max_length=50)
    group = models.CharField(max_length=50, blank=True, null=True)
            
#PANEL    
class Panel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
class PanelUsersManager(models.Manager):
    def create_user(self, first_name, last_name, email, password, panel, group):
        panel_user = self.create(
            first_name=first_name, 
            last_name=last_name,
            email=email,
            password=password,
            panel=panel,
            group=group
        )
        panel_user.save()
        return panel_user

class PanelUsers(models.Model):
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    group = models.CharField(max_length=50, blank=True, null=True)
    
    objects = PanelUsersManager()
    


#ADMIN
class RepositoryFiles(models.Model):
    title = models.CharField(max_length=255)
    proponents = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to="RepositoryFiles/")
    text_file = models.CharField(max_length=255, blank=True, null=True)    
    lsa_matrix = models.BinaryField(null=True) 
    
    class Meta:
        db_table = "db_repository"
        
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class AdminUsersManager(models.Manager):
    def create_user(self, first_name, last_name, email, password, admin, group):
        admin_user = self.create(
            first_name=first_name, 
            last_name=last_name,
            email=email,
            password=password,
            admin=admin,
            group=group
        )
        admin_user.save()
        return admin_user

class AdminUsers(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    group = models.CharField(max_length=50, blank=True, null=True)
    
    objects = AdminUsersManager()
          

class StudentUsers(models.Model):
    sn = models.BigAutoField(primary_key=True, editable=False)
    Student_Id = models.CharField(max_length=255)
    Student_Name = models.CharField(max_length=255)
    Email = models.EmailField()
    Contact_Number = models.CharField(max_length=20, null=True)
    Course = models.CharField(max_length=255)
    SUBJECT_CODE = models.CharField(max_length=255)
    SUBJECT_DESCRIPTION = models.CharField(max_length=255)
    YR_SEC = models.CharField(max_length=255)
    SEM = models.CharField(max_length=255)
    SY = models.CharField(max_length=255)

    class Meta:
        db_table = "user_enrolled_students"
        
class StudentUsersManager(models.Manager):
    def create_user(self, student_id, username, email, password, student, group):
        student_user = self.create(
            first_name=first_name, 
            last_name=last_name,
            email=email,
            password=password,
            student=student,
            group=group
        )
        student_user.save()
        return student_user

#STUDENT
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=255)
    group = models.CharField(max_length=50, blank=True, null=True)
    
    objects = StudentUsersManager()
    
        
#STUDENT DASHBOARD


#UPLOAD FILES FOR SIMILARITY TEST
class TitleDefense(models.Model):
    student_title = models.CharField(max_length=255)
    student_proponents = models.CharField(max_length=255)
    student_pdf_file = models.FileField(upload_to="TitleDefFiles/")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "db_title_docs"
        
class ProposalDefense(models.Model):
    student_title_p = models.CharField(max_length=255)
    student_proponents_p = models.CharField(max_length=255)
    student_pdf_file_p = models.FileField(upload_to="ProposalDefFiles/")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "db_proposal_docs"
        
class FinalDefense(models.Model):
    student_title_f = models.CharField(max_length=255)
    student_proponents_f = models.CharField(max_length=255)
    student_pdf_file_f = models.FileField(upload_to="FinalDefFiles/")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "db_final_docs"
        