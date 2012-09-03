# When implementing a callback, refine the context
# name, from the bulky template, then access the data from that
# callback. The existence of the  appropriate structure will be checked
# during the call, and the client notified of any shortages.

from spray import client


# Used for...
# follower.project.comment
# sponsor.project.comment
def comment_callback(crafter_user_project_system):
    return '[comment]'

comment_callback.token_id = 'comment'
client.register_callback(comment_callback)


# Used for...
# crafter.message.sent
def crafter_email_callback(crafter_user_project_system):
    return '[crafter_email]'

crafter_email_callback.token_id = 'crafter_email'
client.register_callback(crafter_email_callback)


# Used for...
# crafter.project.comment
# crafter.project.drafted
# crafter.project.submitted
# crafter.project.update
# curator.project.curated
# follower.project.comment
# moderator.project.cancelled
# moderator.project.featured
# moderator.project.moderated
# moderator.project.published
# sponsor.message.sent
# sponsor.project.comment
# sponsor.project.fundingtarget
# sponsor.project.milestone1
# sponsor.project.milestone2
# sponsor.project.pledge
# system.payment.processed
# system.payment.processedwithfailures
# system.project.completed.unsuccessful
# system.project.completedsuccessful
# system.project.completedunsuccessful
# system.project.drafted
# system.project.paymentresolved
# system.project.stats
# user.question.sent
def crafter_first_name_callback(crafter_user_project_system):
    return '[crafter_first_name]'

crafter_first_name_callback.token_id = 'crafter_first_name'
client.register_callback(crafter_first_name_callback)


# Used for...
# crafter.project.comment
# crafter.project.update
# moderator.project.published
# sponsor.project.fundingtarget
def crafter_last_name_callback(crafter_user_project_system):
    return '[crafter_last_name]'

crafter_last_name_callback.token_id = 'crafter_last_name'
client.register_callback(crafter_last_name_callback)


# Used for...
# moderator.project.published
def crafter_profile_callback(crafter_user_project_system):
    return '[crafter_profile]'

crafter_profile_callback.token_id = 'crafter_profile'
client.register_callback(crafter_profile_callback)


# Used for...
# moderator.project.published
# sponsor.project.fundingtarget
# sponsor.project.milestone1
# sponsor.project.milestone2
def crafter_twitter_tag_callback(crafter_user_project_system):
    return '[crafter_twitter_tag]'

crafter_twitter_tag_callback.token_id = 'crafter_twitter_tag'
client.register_callback(crafter_twitter_tag_callback)


# Used for...
# crafter.project.curatorrequest
# curator.project.curated
def curator_callback(crafter_user_project_system):
    return '[curator]'

curator_callback.token_id = 'curator'
client.register_callback(curator_callback)


# Used for...
# moderator.project.published
def curator_first_name_callback(crafter_user_project_system):
    return '[curator_first_name]'

curator_first_name_callback.token_id = 'curator_first_name'
client.register_callback(curator_first_name_callback)


# Used for...
# crafter.project.curatorrequest
# curator.project.curated
def curator_url_callback(crafter_user_project_system):
    return '[curator_url]'

curator_url_callback.token_id = 'curator_url'
client.register_callback(curator_url_callback)


# Used for...
# moderator.project.cancelled
# moderator.project.published
# sponsor.project.milestone1
# sponsor.project.milestone2
# system.payment.processed
# system.payment.processedwithfailures
# system.project.completed.unsuccessful
# system.project.completedunsuccessful
# system.project.paymentresolved
# system.project.stats
def dashboard_url_callback(crafter_user_project_system):
    return '[dashboard_url]'

dashboard_url_callback.token_id = 'dashboard_url'
client.register_callback(dashboard_url_callback)


# Used for...
# system.project.monthstats
def date_a_month_yesterday_callback(crafter_user_project_system):
    return '[date_a_month_yesterday]'

date_a_month_yesterday_callback.token_id = 'date_a_month_yesterday'
client.register_callback(date_a_month_yesterday_callback)


# Used for...
# system.project.stats
# system.project.weekstats
def date_a_week_yesterday_callback(crafter_user_project_system):
    return '[date_a_week_yesterday]'

date_a_week_yesterday_callback.token_id = 'date_a_week_yesterday'
client.register_callback(date_a_week_yesterday_callback)


# Used for...
# system.project.daystats
# system.project.monthstats
# system.project.stats
# system.project.weekstats
def date_yesterday_callback(crafter_user_project_system):
    return '[date_yesterday]'

date_yesterday_callback.token_id = 'date_yesterday'
client.register_callback(date_yesterday_callback)


# Used for...
# crafter.project.comment
# crafter.project.update
# moderator.project.featured
def days_remaining_callback(crafter_user_project_system):
    return '[days_remaining]'

days_remaining_callback.token_id = 'days_remaining'
client.register_callback(days_remaining_callback)


# Used for...
# sponsor.project.fundingtarget
# sponsor.project.milestone1
# sponsor.project.milestone2
# system.project.stats
def days_until_completion_date_callback(crafter_user_project_system):
    return '[days_until_completion_date]'

days_until_completion_date_callback.token_id = 'days_until_completion_date'
client.register_callback(days_until_completion_date_callback)


# Used for...
# sponsor.project.preapproval
# system.project.completedunsuccessful
def discover_url_callback(crafter_user_project_system):
    return '[discover_url]'

discover_url_callback.token_id = 'discover_url'
client.register_callback(discover_url_callback)


# Used for...
# user.contactus.sent
def email_callback(crafter_user_project_system):
    return '[email]'

email_callback.token_id = 'email'
client.register_callback(email_callback)


# Used for...
# system.error.*
def error_title_callback(crafter_user_project_system):
    return '[error_title]'

error_title_callback.token_id = 'error_title'
client.register_callback(error_title_callback)


# Used for...
# system.error.*
def event_id_callback(crafter_user_project_system):
    return '[event_id]'

event_id_callback.token_id = 'event_id'
client.register_callback(event_id_callback)


# Used for...
# admins.contactus.received
# sponsor.message.sent
# user.message.sent
def first_name_callback(crafter_user_project_system):
    return '[first_name]'

first_name_callback.token_id = 'first_name'
client.register_callback(first_name_callback)


# Used for...
# crafter.message.sent
# crafter.project.comment
# crafter.project.update
# moderator.project.cancelled
# sponsor.project.fundingtarget
# sponsor.project.milestone1
# sponsor.project.milestone2
# system.project.completedsuccessful
# system.project.completedunsuccessful
def follower_first_name_callback(crafter_user_project_system):
    return '[follower_first_name]'

follower_first_name_callback.token_id = 'follower_first_name'
client.register_callback(follower_first_name_callback)


# Used for...
# moderator.project.published
# sponsor.project.fundingtarget
def institution_callback(crafter_user_project_system):
    return '[institution]'

institution_callback.token_id = 'institution'
client.register_callback(institution_callback)


# Used for...
# moderator.project.published
def institution_twitter_tag_callback(crafter_user_project_system):
    return '[institution_twitter_tag]'

institution_twitter_tag_callback.token_id = 'institution_twitter_tag'
client.register_callback(institution_twitter_tag_callback)


# Used for...
# sponsor.message.sent
def last_name_callback(crafter_user_project_system):
    return '[last_name]'

last_name_callback.token_id = 'last_name'
client.register_callback(last_name_callback)


# Used for...
# crafter.message.sent
# sponsor.message.sent
# user.countryrequest.sent
# user.message.sent
# user.question.sent
# user.report.sent
def message_callback(crafter_user_project_system):
    return '[message]'

message_callback.token_id = 'message'
client.register_callback(message_callback)


# Used for...
# user.contactus.sent
def message_data_callback(crafter_user_project_system):
    return '[message_data]'

message_data_callback.token_id = 'message_data'
client.register_callback(message_data_callback)


# Used for...
# moderator.project.moderated
def moderation_table_callback(crafter_user_project_system):
    return '[moderation_table]'

moderation_table_callback.token_id = 'moderation_table'
client.register_callback(moderation_table_callback)


# Used for...
# user.contactus.sent
def name_callback(crafter_user_project_system):
    return '[name]'

name_callback.token_id = 'name'
client.register_callback(name_callback)


# Used for...
# sponsor.project.preapproval
# system.payment.failed
# system.payment.successful
# system.project.completedsuccessful
# system.project.completedsuccessfulbutnoreward
def next_milestone_callback(crafter_user_project_system):
    return '[next_milestone]'

next_milestone_callback.token_id = 'next_milestone'
client.register_callback(next_milestone_callback)


# Used for...
# system.error.*
def node_id_callback(crafter_user_project_system):
    return '[node_id]'

node_id_callback.token_id = 'node_id'
client.register_callback(node_id_callback)


# Used for...
# system.project.stats
def page_views_callback(crafter_user_project_system):
    return '[page_views]'

page_views_callback.token_id = 'page_views'
client.register_callback(page_views_callback)


# Used for...
# admins.payment.processed
# system.project.paymentresolved
def payment_name_callback(crafter_user_project_system):
    return '[payment_name]'

payment_name_callback.token_id = 'payment_name'
client.register_callback(payment_name_callback)


# Used for...
# system.payment.failed
# system.project.paymentresolved
def payment_url_callback(crafter_user_project_system):
    return '[payment_url]'

payment_url_callback.token_id = 'payment_url'
client.register_callback(payment_url_callback)


# Used for...
# system.project.stats
def percentage_raised_last_week_callback(crafter_user_project_system):
    return '[percentage_raised_last_week]'

percentage_raised_last_week_callback.token_id = 'percentage_raised_last_week'
client.register_callback(percentage_raised_last_week_callback)


# Used for...
# admins.payment.processed
# sponsor.project.pledge
# system.payment.failed
# system.payment.successful
# system.project.paymentresolved
def pledge_amount_callback(crafter_user_project_system):
    return '[pledge_amount]'

pledge_amount_callback.token_id = 'pledge_amount'
client.register_callback(pledge_amount_callback)


# Used for...
# system.project.stats
def pledged_last_week_callback(crafter_user_project_system):
    return '[pledged_last_week]'

pledged_last_week_callback.token_id = 'pledged_last_week'
client.register_callback(pledged_last_week_callback)


# Used for...
# admins.payment.processed
def pledges_callback(crafter_user_project_system):
    return '[pledges]'

pledges_callback.token_id = 'pledges'
client.register_callback(pledges_callback)


# Used for...
# admins.payment.processed
# system.project.paymentresolved
def pledges_failed_callback(crafter_user_project_system):
    return '[pledges_failed]'

pledges_failed_callback.token_id = 'pledges_failed'
client.register_callback(pledges_failed_callback)


# Used for...
# system.project.stats
def pledges_last_week_callback(crafter_user_project_system):
    return '[pledges_last_week]'

pledges_last_week_callback.token_id = 'pledges_last_week'
client.register_callback(pledges_last_week_callback)


# Used for...
# system.project.paymentresolved
def pledges_resolved_callback(crafter_user_project_system):
    return '[pledges_resolved]'

pledges_resolved_callback.token_id = 'pledges_resolved'
client.register_callback(pledges_resolved_callback)


# Used for...
# admins.payment.processed
def pledges_successful_callback(crafter_user_project_system):
    return '[pledges_successful]'

pledges_successful_callback.token_id = 'pledges_successful'
client.register_callback(pledges_successful_callback)


# Used for...
# moderator.project.published
def primary_category_callback(crafter_user_project_system):
    return '[primary_category]'

primary_category_callback.token_id = 'primary_category'
client.register_callback(primary_category_callback)


# Used for...
# crafter.project.comment
# moderator.project.featured
def project_comment_url_callback(crafter_user_project_system):
    return '[project_comment_url]'

project_comment_url_callback.token_id = 'project_comment_url'
client.register_callback(project_comment_url_callback)


# Used for...
# follower.project.comment
# sponsor.project.comment
def project_comments_url_callback(crafter_user_project_system):
    return '[project_comments_url]'

project_comments_url_callback.token_id = 'project_comments_url'
client.register_callback(project_comments_url_callback)


# Used for...
# admins.payment.processed
# crafter.message.sent
# crafter.project.curatorrequest
# crafter.project.submitted
# crafter.project.update
# curator.project.curated
# moderator.project.cancelled
# moderator.project.featured
# moderator.project.published
# sponsor.project.fundingtarget
# sponsor.project.milestone1
# sponsor.project.milestone2
# sponsor.project.pledge
# sponsor.project.preapproval
# system.payment.failed
# system.payment.successful
# system.project.completed.unsuccessful
# system.project.completedsuccessful
# system.project.completedsuccessfulbutnoreward
# system.project.completedunsuccessful
# system.project.paymentresolved
def project_name_callback(crafter_user_project_system):
    return '[project_name]'

project_name_callback.token_id = 'project_name'
client.register_callback(project_name_callback)


# Used for...
# crafter.project.drafted
# crafter.project.submitted
# system.project.drafted
def project_preview_url_callback(crafter_user_project_system):
    return '[project_preview_url]'

project_preview_url_callback.token_id = 'project_preview_url'
client.register_callback(project_preview_url_callback)


# Used for...
# crafter.project.update
def project_update_url_callback(crafter_user_project_system):
    return '[project_update_url]'

project_update_url_callback.token_id = 'project_update_url'
client.register_callback(project_update_url_callback)


# Used for...
# crafter.project.drafted
# moderator.project.cancelled
# moderator.project.published
# sponsor.project.fundingtarget
# sponsor.project.milestone1
# sponsor.project.milestone2
# sponsor.project.pledge
# system.payment.failed
# system.payment.successful
# system.project.completedsuccessful
# system.project.completedsuccessfulbutnoreward
# system.project.completedunsuccessful
def project_url_callback(crafter_user_project_system):
    return '[project_url]'

project_url_callback.token_id = 'project_url'
client.register_callback(project_url_callback)


# Used for...
# sponsor.project.pledge
def project_vanity_callback(crafter_user_project_system):
    return '[project_vanity]'

project_vanity_callback.token_id = 'project_vanity'
client.register_callback(project_vanity_callback)


# Used for...
# system.project.monthstats
def projects_failed_last_month_callback(crafter_user_project_system):
    return '[projects_failed_last_month]'

projects_failed_last_month_callback.token_id = 'projects_failed_last_month'
client.register_callback(projects_failed_last_month_callback)


# Used for...
# system.project.weekstats
def projects_failed_last_week_callback(crafter_user_project_system):
    return '[projects_failed_last_week]'

projects_failed_last_week_callback.token_id = 'projects_failed_last_week'
client.register_callback(projects_failed_last_week_callback)


# Used for...
# system.project.daystats
def projects_failed_yesterday_callback(crafter_user_project_system):
    return '[projects_failed_yesterday]'

projects_failed_yesterday_callback.token_id = 'projects_failed_yesterday'
client.register_callback(projects_failed_yesterday_callback)


# Used for...
# system.project.monthstats
def projects_funding_target_last_month_callback(crafter_user_project_system):
    return '[projects_funding_target_last_month]'

projects_funding_target_last_month_callback.token_id = 'projects_funding_target_last_month'
client.register_callback(projects_funding_target_last_month_callback)


# Used for...
# system.project.weekstats
def projects_funding_target_last_week_callback(crafter_user_project_system):
    return '[projects_funding_target_last_week]'

projects_funding_target_last_week_callback.token_id = 'projects_funding_target_last_week'
client.register_callback(projects_funding_target_last_week_callback)


# Used for...
# system.project.daystats
def projects_funding_target_yesterday_callback(crafter_user_project_system):
    return '[projects_funding_target_yesterday]'

projects_funding_target_yesterday_callback.token_id = 'projects_funding_target_yesterday'
client.register_callback(projects_funding_target_yesterday_callback)


# Used for...
# system.project.monthstats
def projects_milestone1_last_month_callback(crafter_user_project_system):
    return '[projects_milestone1_last_month]'

projects_milestone1_last_month_callback.token_id = 'projects_milestone1_last_month'
client.register_callback(projects_milestone1_last_month_callback)


# Used for...
# system.project.weekstats
def projects_milestone1_last_week_callback(crafter_user_project_system):
    return '[projects_milestone1_last_week]'

projects_milestone1_last_week_callback.token_id = 'projects_milestone1_last_week'
client.register_callback(projects_milestone1_last_week_callback)


# Used for...
# system.project.daystats
def projects_milestone1_yesterday_callback(crafter_user_project_system):
    return '[projects_milestone1_yesterday]'

projects_milestone1_yesterday_callback.token_id = 'projects_milestone1_yesterday'
client.register_callback(projects_milestone1_yesterday_callback)


# Used for...
# system.project.monthstats
def projects_milestone2_last_month_callback(crafter_user_project_system):
    return '[projects_milestone2_last_month]'

projects_milestone2_last_month_callback.token_id = 'projects_milestone2_last_month'
client.register_callback(projects_milestone2_last_month_callback)


# Used for...
# system.project.weekstats
def projects_milestone2_last_week_callback(crafter_user_project_system):
    return '[projects_milestone2_last_week]'

projects_milestone2_last_week_callback.token_id = 'projects_milestone2_last_week'
client.register_callback(projects_milestone2_last_week_callback)


# Used for...
# system.project.daystats
def projects_milestone2_yesterday_callback(crafter_user_project_system):
    return '[projects_milestone2_yesterday]'

projects_milestone2_yesterday_callback.token_id = 'projects_milestone2_yesterday'
client.register_callback(projects_milestone2_yesterday_callback)


# Used for...
# system.project.monthstats
def projects_published_last_month_callback(crafter_user_project_system):
    return '[projects_published_last_month]'

projects_published_last_month_callback.token_id = 'projects_published_last_month'
client.register_callback(projects_published_last_month_callback)


# Used for...
# system.project.weekstats
def projects_published_last_week_callback(crafter_user_project_system):
    return '[projects_published_last_week]'

projects_published_last_week_callback.token_id = 'projects_published_last_week'
client.register_callback(projects_published_last_week_callback)


# Used for...
# system.project.daystats
def projects_published_yesterday_callback(crafter_user_project_system):
    return '[projects_published_yesterday]'

projects_published_yesterday_callback.token_id = 'projects_published_yesterday'
client.register_callback(projects_published_yesterday_callback)


# Used for...
# system.project.monthstats
def projects_submitted_last_month_callback(crafter_user_project_system):
    return '[projects_submitted_last_month]'

projects_submitted_last_month_callback.token_id = 'projects_submitted_last_month'
client.register_callback(projects_submitted_last_month_callback)


# Used for...
# system.project.weekstats
def projects_submitted_last_week_callback(crafter_user_project_system):
    return '[projects_submitted_last_week]'

projects_submitted_last_week_callback.token_id = 'projects_submitted_last_week'
client.register_callback(projects_submitted_last_week_callback)


# Used for...
# system.project.daystats
def projects_submitted_yesterday_callback(crafter_user_project_system):
    return '[projects_submitted_yesterday]'

projects_submitted_yesterday_callback.token_id = 'projects_submitted_yesterday'
client.register_callback(projects_submitted_yesterday_callback)


# Used for...
# moderator.project.published
def promotion_checklist_url_callback(crafter_user_project_system):
    return '[promotion_checklist_url]'

promotion_checklist_url_callback.token_id = 'promotion_checklist_url'
client.register_callback(promotion_checklist_url_callback)


# Used for...
# system.project.completed.unsuccessful
# system.project.completedsuccessful
# system.project.completedunsuccessful
def questionnaire_url_callback(crafter_user_project_system):
    return '[questionnaire_url]'

questionnaire_url_callback.token_id = 'questionnaire_url'
client.register_callback(questionnaire_url_callback)


# Used for...
# user.report.sent
def reported_url_callback(crafter_user_project_system):
    return '[reported_url]'

reported_url_callback.token_id = 'reported_url'
client.register_callback(reported_url_callback)


# Used for...
# sponsor.project.milestone1
# sponsor.project.milestone2
def rewards_unlocked_callback(crafter_user_project_system):
    return '[rewards_unlocked]'

rewards_unlocked_callback.token_id = 'rewards_unlocked'
client.register_callback(rewards_unlocked_callback)


# Used for...
# crafter.message.sent
# crafter.project.comment
# crafter.project.update
# follower.project.comment
# moderator.project.cancelled
# sponsor.project.comment
# sponsor.project.fundingtarget
# sponsor.project.milestone1
# sponsor.project.milestone2
# sponsor.project.pledge
# sponsor.project.preapproval
# system.payment.failed
# system.payment.successful
# system.project.completedsuccessfulbutnoreward
# system.project.completedunsuccessful
def sponsor_first_name_callback(crafter_user_project_system):
    return '[sponsor_first_name]'

sponsor_first_name_callback.token_id = 'sponsor_first_name'
client.register_callback(sponsor_first_name_callback)


# Used for...
# follower.project.comment
# sponsor.project.comment
def sponsor_last_name_callback(crafter_user_project_system):
    return '[sponsor_last_name]'

sponsor_last_name_callback.token_id = 'sponsor_last_name'
client.register_callback(sponsor_last_name_callback)


# Used for...
# user.contactus.sent
def subject_callback(crafter_user_project_system):
    return '[subject]'

subject_callback.token_id = 'subject'
client.register_callback(subject_callback)


# Used for...
# system.project.monthstats
def total_pledged_last_month_callback(crafter_user_project_system):
    return '[total_pledged_last_month]'

total_pledged_last_month_callback.token_id = 'total_pledged_last_month'
client.register_callback(total_pledged_last_month_callback)


# Used for...
# system.project.weekstats
def total_pledged_last_week_callback(crafter_user_project_system):
    return '[total_pledged_last_week]'

total_pledged_last_week_callback.token_id = 'total_pledged_last_week'
client.register_callback(total_pledged_last_week_callback)


# Used for...
# system.project.daystats
def total_pledged_yesterday_callback(crafter_user_project_system):
    return '[total_pledged_yesterday]'

total_pledged_yesterday_callback.token_id = 'total_pledged_yesterday'
client.register_callback(total_pledged_yesterday_callback)


# Used for...
# system.project.monthstats
def total_pledges_last_month_callback(crafter_user_project_system):
    return '[total_pledges_last_month]'

total_pledges_last_month_callback.token_id = 'total_pledges_last_month'
client.register_callback(total_pledges_last_month_callback)


# Used for...
# system.project.weekstats
def total_pledges_last_week_callback(crafter_user_project_system):
    return '[total_pledges_last_week]'

total_pledges_last_week_callback.token_id = 'total_pledges_last_week'
client.register_callback(total_pledges_last_week_callback)


# Used for...
# system.project.daystats
def total_pledges_yesterday_callback(crafter_user_project_system):
    return '[total_pledges_yesterday]'

total_pledges_yesterday_callback.token_id = 'total_pledges_yesterday'
client.register_callback(total_pledges_yesterday_callback)


# Used for...
# system.error.*
def traceback_callback(crafter_user_project_system):
    return '[traceback]'

traceback_callback.token_id = 'traceback'
client.register_callback(traceback_callback)


# Used for...
# sponsor.message.sent
# user.countryrequest.sent
# user.message.sent
# user.question.sent
# user.report.sent
def user_email_callback(crafter_user_project_system):
    return '[user_email]'

user_email_callback.token_id = 'user_email'
client.register_callback(user_email_callback)


# Used for...
# crafter.project.drafted
# user.countryrequest.sent
# user.question.sent
# user.report.sent
def user_name_callback(crafter_user_project_system):
    return '[user_name]'

user_name_callback.token_id = 'user_name'
client.register_callback(user_name_callback)


# Used for...
# crafter.message.sent
# sponsor.message.sent
# user.contactus.sent
# user.countryrequest.sent
# user.message.sent
# user.question.sent
# user.report.sent
def username_callback(crafter_user_project_system):
    return '[username]'

username_callback.token_id = 'username'
client.register_callback(username_callback)


# Used for...
# system.project.monthstats
def website_page_views_last_month_callback(crafter_user_project_system):
    return '[website_page_views_last_month]'

website_page_views_last_month_callback.token_id = 'website_page_views_last_month'
client.register_callback(website_page_views_last_month_callback)


# Used for...
# system.project.weekstats
def website_page_views_last_week_callback(crafter_user_project_system):
    return '[website_page_views_last_week]'

website_page_views_last_week_callback.token_id = 'website_page_views_last_week'
client.register_callback(website_page_views_last_week_callback)


# Used for...
# system.project.daystats
def website_page_views_yesterday_callback(crafter_user_project_system):
    return '[website_page_views_yesterday]'

website_page_views_yesterday_callback.token_id = 'website_page_views_yesterday'
client.register_callback(website_page_views_yesterday_callback)

