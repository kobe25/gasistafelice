from django.db import models

from django.utils.translation import ugettext_lazy as _, string_concat, ugettext
from django.contrib.auth.models import User, Group

from flexi_auth.models import ParamRole, PrincipalParamRoleRelation

from django.db.models.signals import post_save, post_delete

class UserProfile(models.Model):

    user = models.OneToOneField(User, unique=True)
    # NULL role can happen if all his roles are deleted
    default_role = models.ForeignKey(ParamRole, null=True)

    def __unicode__(self):
        return _("Profile for %(user)s") % { 'user' : self.user }

    def save(self, *args, **kw):
        p = UserProfile.objects.get(pk=self.pk)
        print "BBB", p, "----", p.default_role
        super(UserProfile, self).save(*args, **kw)
        print "CCC", self, "----", self.default_role

#-----------------------------------------------------------------------------#
# SIGNALS                                                                     #
#-----------------------------------------------------------------------------#

def set_default_role(u, ppr):
    """
    Setting default role for user.
    This consequently updates the user default home page...
    """

    try:
        profile = UserProfile.objects.get(user=u)
    except UserProfile.DoesNotExist as e:
        profile = UserProfile(user=u)

    if profile.default_role != ppr.role:
        log.debug("Updating default role: %s -> %s" % (profile.default_role, ppr.role))
        profile.default_role = ppr.role
        profile.save()


def set_default_role_if_deleted(u, deleted_ppr):
    """Check if role set is the one that was just deleted."""

    if u.get_profile().default_role == deleted_ppr.role:
        try:
            new_ppr = u.principal_param_role_set.all()[0]
        except IndexError:
            new_ppr = None
        set_default_role(u, new_ppr)

#--------------------------------------------------------------------------------

def on_ppr_save_set_default_role(sender, **kwargs):

    ppr = kwargs['instance']
    created = kwargs['created']

    p = ppr.principal #Principal can be a User or a Group

    if created:
        # Set default role for user if it is not set

        if isinstance(p, Group):

            for u in p.user_set.all():
                set_default_role(u, ppr)

        else:
            set_default_role(p, ppr)

def on_ppr_delete_reset_default_role(sender, **kwargs):

    deleted_ppr = kwargs['instance']
    p = deleted_ppr.principal #Principal can be a User or a Group

    # Reset default role for user if it is not set

    if isinstance(p, Group):

        for u in p.user_set.all():
            set_default_role_if_deleted(u, deleted_ppr)

    else:
        set_default_role_if_deleted(p, deleted_ppr)


post_save.connect(on_ppr_save_set_default_role, sender=PrincipalParamRoleRelation)
post_delete.connect(on_ppr_delete_reset_default_role, sender=PrincipalParamRoleRelation)
