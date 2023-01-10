from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin_register/", views.admin_register, name="admin_register"),
    
    #DOCUMENT SIMILARITY DOCUMENTS URLS
    path("TableTitle/", views.TableTitle, name="TableTitle"),
    path("TableProposal/", views.TableProposal, name="TableProposal"),
    path("TableFinal/", views.TableFinal, name="TableFinal"),
    
    # repository
    path("AddRepositoryFiles/", views.AddRepositoryFiles, name="AddRepositoryFiles"),
    path("ViewRepositoryFiles/<int:id>", views.ViewRepositoryFiles),
    path("EditRepositoryFiles/<int:id>", views.EditRepositoryFiles),
    path("DeleteRepositoryFiles/<int:id>", views.DeleteRepositoryFiles),
    path("dashboard/TableRepository/", views.TableRepository, name="TableRepository"),
    
    # enrolled students
    path("EnrolledStudentsExcel/", views.EnrolledStudentsExcel, name="EnrolledStudentsExcel"),
    path("EditStudentsDetails/<int:sn>", views.EditStudentsDetails),
    path("ViewStudentDetails/", views.ViewStudentDetails),
    path("DeleteEnrolledStudent/<int:sn>", views.DeleteEnrolledStudent),
    path("TableEnrolledUsers/", views.TableEnrolledUsers, name="TableEnrolledUsers"),
    path("TableRegisteredStudents/", views.TableRegisteredStudents, name="TableRegisteredStudents"),
    
    # students
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
    #upload student documents
    path("upload_title_defense/", views.upload_title_defense, name="upload_title_defense"),
    path("upload_proposal_defense/", views.upload_proposal_defense, name="upload_proposal_defense"),
    path("upload_final_defense/", views.upload_final_defense, name="upload_final_defense"),
    
    #view student documents
    path("view_title_defense/", views.view_title_defense, name="view_title_defense"),
    
    #register student user
    path("search_student_id", views.search_student_id, name="search_student_id"),
    path("search_student_id/register_student", views.register_student, name="register_student"),
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    #panel
    path("panel_dashboard/", views.panel_dashboard, name="panel_dashboard"),
    path("panel_register/", views.panel_register, name="panel_register"),
    path("uploaded_title_docs/", views.uploaded_title_docs, name="uploaded_title_docs"),
    path("uploaded_proposal_docs/", views.uploaded_proposal_docs, name="uploaded_proposal_docs"),
    path("uploaded_final_docs/", views.uploaded_final_docs, name="uploaded_final_docs"),
    path("TableRegisteredPanels/", views.TableRegisteredPanels, name="TableRegisteredPanels"),
    
]
