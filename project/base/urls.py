
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("Login/", views.login_user, name="login"),
    path("Logout/", views.logout_user, name="logout"),
    path("SignUp/", views.register_user, name="signup"),
    path("User-Setting/", views.user_settings, name="user_setting"),

    path("User-Setting/Update-User", views.update_user, name="update_user"),

    path("Print/", views.print_view, name="print"),
    path("Print-Permit/", views.generate_permit_pdf, name="print_permit"),

    path("Logs/", views.logger, name="logger"),

    path("INB-Dashboard/", views.inb_data_visualization, name="inb-dashboard"),
    
    path("INB-Dashboard/Gender/", views.gender_summary, name="inb-gender-summary"),
    path("INB-Dashboard/Barangay/", views.barangay_summary, name="inb-barangay-summary"),
    path("INB-Dashboard/Active-Scholar/", views.active_scholar_summary, name="inb-active-scholar-summary"),
    path("INB-Dashboard/Graduated-Scholar/", views.graduate_scholar_summary, name="inb-graduated-scholar-summary"),
    path("INB-Dashboard/Unsuccessful-Scholar/", views.unsuccessful_scholar_summary, name="inb-unsuccessful-scholar-summary"),
    path("INB-Dashboard/Applied-Admitted-Scholar/", views.tracker_scholar_summary, name="inb-tracker-scholar-summary"),
    path("INB-Dashboard/School-Grantees-Scholar/", views.school_scholar_summary, name="inb-school-scholar-summary"),
    path("INB-Dashboard/Course-Grantees-Scholar/", views.course_scholar_summary, name="inb-course-scholar-summary"),
    path("INB-Dashboard/Year-Level-Scholar/", views.yearlevel_scholar_summary, name="inb-year-scholar-summary"),
    
    path("inb/passed/applicant_info/<str:control_number>",views.inb_applicant_information_details,name="inb_applicant_information_details"),

    
    



    path("FA-Dashboard/", views.fa_data_visualization, name="fa-dashboard"),

    path("CSV_Record", views.csv_record, name="export"),
    

    
    path('delete_applicant_id/<int:pk>/<str:model_name>/', views.delete_by_id, name='delete_applicant_id'),
    path('delete_applicant/<str:control_number>/<str:model_name>/', views.delete_by_control_number, name='delete_applicant'),

    
    path("Applicant_List/", views.iskolar_ng_bayan_list, name="inb_applicant_list"),
    path("Iskolar_ng_Binan_List/Add",views.add_information, {"form_type": "applicant"}, name="add_inb_applicant",),

    path("Financial_Assistance_List/",views.financial_assistance_list,name="fa_applicant_list",),
    path("Financial_Assistance_List/Add",views.add_information,{"form_type": "financial_assistance"},name="add_fa_applicant",),

    path("Update_INB_Record/<int:pk>", views.update_information, name="update_inb_record"),
    path("Update_FA_Record/<int:pk>", views.update_information, name="update_fa_record"),
    # ------------------------------------------------------------------------------------------------------------------------------

  
    path("INB_Applicant_Info/<int:pk>/",views.inb_applicant_information,name="inb_applicant_info",),
    path("inb_requirements_list/<str:control_number>",views.inb_requirements_list,name="inb_requirements_list",),
    path("inb_filter_applicants/",views.inb_filter_applicants,name="inb_filter_applicants",),

    path("inb/pending/applicant/",views.inb_applicant_list,{"status": "pending"},name="inb_pending_applicant",),

    path("inb_filter_assessment",views.inb_filter_assessment,name="inb_filter_assessment",),
   

    path("update_assessment/<str:control_number>/", views.inb_applicant_info, {"status": "pending"}, name="update_assessment"),
    path("inb/pending/applicant/<str:control_number>/", views.inb_applicant_info, {"status": "pending"}, name="inb_pending_applicant_info"),

    path("inb/passed/applicant/",views.inb_applicant_list,{"status": "passed"},name="inb_passed_applicant",),
    path("inb/passed/applicant_info/<str:control_number>/",views.inb_applicant_info,{"status": "passed"},name="inb_passed_applicant_info",),
    path("inb/failed/applicant/",views.inb_applicant_list,{"status": "failed"},name="inb_failed_applicant",),
    path("inb/failed/applicant_info/<str:control_number>/",views.inb_applicant_info,{"status": "failed"},name="inb_failed_applicant_info",),


    # -------------------------------------------------------------------------------------------------------------------------------
    path("Financial_Assistance_List/",views.financial_assistance_list,name="fa_applicant_list",),

    path("FA_Applicant_Info/<int:pk>/",views.fa_applicant_information,name="fa_applicant_info",),

    path("fa_filter_applicants/", views.fa_filter_applicants, name="fa_filter_applicants"),
    path("FA_Requirements/<str:control_number>/",views.fa_requirement_list,name="fa_requirements_list",),

    path("fa/pending/applicant/",views.fa_applicant_list,{"status": "pending"},name="fa_pending_applicant",),

     path("fa_filter_assessment",views.fa_filter_assessment,name="fa_filter_applicants",),


    path("fa/pending/applicant/<str:control_number>/", views.fa_applicant_info, {"status": "pending"}, name="fa_pending_applicant_info"),

    path("fa/passed/applicant/",views.fa_applicant_list,{"status": "passed"},name="fa_passed_applicant",),
    path("fa/passed/applicant_info/<str:control_number>/",views.fa_applicant_info,{"status": "passed"},name="fa_passed_applicant_info",),
    path("fa/failed/applicant/",views.fa_applicant_list,{"status": "failed"},name="fa_failed_applicant",),
    path("fa/failed/applicant_info/<str:control_number>/",views.fa_applicant_info,{"status": "failed"},name="fa_failed_applicant_info",),

    
    
    
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

    path('delete_requirement/<str:item_type>/<int:item_id>/', views.delete_requirement, name='delete_requirement'),
   

   path('import-grade/', views.import_grade, name='import_excel'),
   path("import_applicant/", views.import_excel, name="import_applicant"),

 
    path('Filter/', views.filter, name='filter'),

    


    path("Page_not_found",views.page_not_found,name="page_not_found"),
]