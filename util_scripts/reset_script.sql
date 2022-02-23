-- RESET script
delete from main_quizrunanswers;
delete from main_quizrun;
delete from main_profile where user_id <> 1;
delete from public.main_educationcenter;
delete from public.auth_user where id <> 1;
