from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("Login/", views.login_user, name="login"),
    path("Logout/", views.logout_user, name="logout"),
    path("SignUp/", views.register_user, name="signup"),
    path("Dashboard/", views.data_visualization, name="dashboard"),
    path("CSV_Record", views.csv_record, name="export"),
    #path("Import_File/", views.import_excel, name="import"),

    
    path('delete_applicant_id/<int:pk>/<str:model_name>/', views.delete_by_id, name='delete_applicant_id'),
    path('delete_applicant/<str:control_number>/<str:model_name>/', views.delete_by_control_number, name='delete_applicant'),

    
    path("Applicant_List/", views.iskolar_ng_bayan_list, name="inb_applicant_list"),
    path("Applicant_List/Add",views.add_information, {"form_type": "applicant"}, name="add_inb_applicant",),

    path("Financial_Assistance_List/",views.financial_assistance_list,name="fa_applicant_list",),
    path("Add_FinancialAssistance_Applicant/",views.add_information,{"form_type": "financial_assistance"},name="add_fa_applicant",),

    path("Update_INB_Record/<int:pk>", views.update_information, name="update_inb_record"),
    path("Update_FA_Record/<int:pk>", views.update_information, name="update_fa_record"),
    # ------------------------------------------------------------------------------------------------------------------------------

  
    path("INB_Applicant_Info/<int:pk>/",views.inb_applicant_information,name="inb_applicant_info",),
    path("inb_requirements_list/<str:control_number>",views.inb_requirements_list,name="inb_requirements_list",),
    path("inb_filter_applicants/",views.inb_filter_applicants,name="inb_filter_applicants",),

    path("inb/passed/applicant/",views.inb_applicant_list,{"status": "passed"},name="inb_passed_applicant",),
    path("inb/passed/applicant_info/<str:control_number>/",views.inb_applicant_info,{"status": "passed"},name="inb_passed_applicant_info",),
    path("inb/failed/applicant/",views.inb_applicant_list,{"status": "failed"},name="inb_failed_applicant",),
    path("inb/failed/applicant_info/<str:control_number>/",views.inb_applicant_info,{"status": "failed"},name="inb_failed_applicant_info",),


    # -------------------------------------------------------------------------------------------------------------------------------
    path("Financial_Assistance_List/",views.financial_assistance_list,name="fa_applicant_list",),

    path("FA_Applicant_Info/<int:pk>/",views.fa_applicant_information,name="fa_applicant_info",),

    path("fa_filter_applicants/", views.fa_filter_applicants, name="fa_filter_applicants"),
    path("FA_Requirements/<str:control_number>/",views.fa_requirement_list,name="fa_requirements_list",),

    path("fa/<str:status>/applicant_info/<str:control_number>/",views.fa_applicant_info,name="fa_applicant_info",),

    path("fa/passed/applicant/",views.fa_applicant_list,{"status": "passed"},name="fa_passed_applicant",),
    path("fa/passed/applicant_info/<str:control_number>/",views.fa_applicant_info,{"status": "passed"},name="fa_passed_applicant_info",),
    path("fa/failed/applicant/",views.fa_applicant_list,{"status": "failed"},name="fa_failed_applicant",),
    path("fa/failed/applicant_info/<str:control_number>/",views.fa_applicant_info,{"status": "failed"},name="fa_failed_applicant_info",),

    path("test1", views.test1, name="forms",),
    
    
    path("School_List/", views.school_course_list, name="sc_list",),
    path("Add_School/", views.create_school, name="create_school"),
    path("Add_Course/", views.add_course, name="create_course" ),
    path("Update_List/", views.update_list, name="update_list"),
    path('delete_item/<str:item_type>/<int:item_id>/', views.delete_item, name='delete_item'),
    path("Update_School_List/<int:school_id>/", views.update_school_list, name="update_school_list"),
    path("Update_Course_List/<int:course_id>/", views.update_course_list, name="update_course_list"),

   

    path("View_Requirements/", views.update_requirement, name="update_req"),
    path("add_requirement/<str:form_type>/", views.add_requirement, name="add_requirement"),

    path("Iskolar_ng_Bayan_Requirement/", views.render_requirement, {"form_type": "inb"}, name="inb_requirement"),
    path("Update_IskolarngBayan_Requirement/<int:requirement_id>/", views.update_inb_requirement, name="update_inb_requirement"),

    path("Financial_Assistance_Requirement/",views.render_requirement, {"form_type": "fa"}, name="fa_requirement",),
    path("Update_FinancialAssistance_Requirement/<int:requirement_id>/", views.update_fa_requirement, name="update_fa_requirement"),

    path('delete_requirements/<str:item_type>/<int:item_id>/', views.delete_requirements, name='delete_requirements'),

    
    path("Filter/", views.filter, name="filter"),
    path("Pending/", views.inb_pending_assesment, name="inb_pending"),
]
