<%inherit file="base.mako"/>
<%def name="title()">Dashboard</%def>

<%def name="content()">
% if disk_saving_mode:
    <div class="alert alert-info"><strong>NOTICE: </strong>Forks, registrations, and uploads will be temporarily disabled while the OSF undergoes a hardware upgrade. These features will return shortly. Thank you for your patience.</div>
% endif
<div class="row">
    <div class="col-sm-7">
        <div>
          <h3>Projects </h3>
            <hr />
        </div><!-- end div -->


    </div><!-- end col -->


</div><!-- end row -->
%if 'badges' in addons_enabled:
    <div class="row">
        <div class="col-sm-5">
            <div class="page-header">
              <button class="btn btn-primary pull-right" id="newBadge" type="button">New Badge</button>
                <h3>Your Badges</h3>
            </div>
            <div mod-meta='{
                     "tpl": "../addons/badges/templates/dashboard_badges.mako",
                     "uri": "/api/v1/dashboard/get_badges/",
                     "replace": true
                }'></div>
        </div>
        <div class="col-sm-5">
            <div class="page-header">
                <h3>Badges You've Awarded</h3>
            </div>
        </div><!-- end col -->
    </div><!-- end row -->
%endif
</%def>

<%def name="stylesheets()">
    ${parent.stylesheets()}
    <link rel="stylesheet" href="/static/css/pages/dashboard-page.css">
</%def>

<%def name="javascript_bottom()">
<script>
    window.contextVars = $.extend(true, {}, window.contextVars, {
        currentUser: {
            'id': '${user_id}'
        }
    });
</script>
<script src=${"/static/public/js/dashboard-page.js" | webpack_asset}></script>

</%def>
