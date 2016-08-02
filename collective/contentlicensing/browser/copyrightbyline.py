from zope.publisher.browser import BrowserView
from zope.component import getUtility, getMultiAdapter
from zope.i18n import translate
from collective.contentlicensing.utilities.interfaces import IContentLicensingUtility
from Products.CMFPlone.utils import getToolByName, safe_unicode
from collective.contentlicensing import ContentLicensingMessageFactory as _
from DateTime import DateTime

class CopyrightBylineView(BrowserView):
    """ Render the copyright byline """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.props = self.context.portal_url.portal_properties.content_licensing_properties
        self.clutil = getUtility(IContentLicensingUtility)

    def getLicenseByline(self):
        """ Get the license byline fields for an object. """
        copyright = self.context.Rights()
        if not copyright:
            copyright = self.props.DefaultSiteCopyright
        holder, license = self.clutil.getLicenseAndHolderFromObject(self.context)
        holder_fullname = ''
        if '(site default)' == holder:
            holder = self.context.Creator()
            mtool = self.context.portal_membership
            mem = mtool.getMemberById(holder)
            try:
                holder_fullname = mem.getProperty('fullname')
            except AttributeError:
                holder = self.props.DefaultSiteCopyrightHolder
        if 'Site Default' == license[0]:
            license = self.props.DefaultSiteLicense
        license_name = license[1]
        if not license_name or 'None' == license_name:
            license_name = ''
        if 'Creative Commons License' == license[0]:
            license_name = license[0]
        license_url = license[2]
        if not license_url or 'None' == license_url:
            license_url = ''
        license_button = license[3]
        if not license_button or 'None' == license_button:
            license_button = ''

        return copyright, translate(holder.decode('utf-8','ignore'), domain="ContentLicensing", target_language=self.request.LANGUAGE), license_name, license_url, license_button, holder_fullname

    def getAlertMsg(self):
        """Use this domain for translation"""
        msg = _(
            _(u'The citation for this resource is presented in APA format. '
            'Copy the citation to your clipboard for reuse.')
        )
        return translate(msg, domain="ContentLicensing", target_language=self.request.LANGUAGE)

    def getCitationInfo(self):
        """ Gets the citation information """

        # Title
        title = self.context.title

        # Creators
        mtool = self.context.portal_membership
        
        def get_fullname(mtool, memid):
            mem = mtool.getMemberById(memid)
            try:
                fullname = mem.getProperty('fullname')
            except AttributeError:
                fullname = memid
            return fullname

        creator = ', '.join([get_fullname(mtool, cr.strip()) \
                                for cr in self.context.Creators()])
        # if creator:
        #     creator = creator + '.'
         
        portal_url = getToolByName(self.context, 'portal_url')
        portal_name = portal_url.getPortalObject().title
        plone_view = getMultiAdapter((self.context, self.request), name='plone')
        create_date = plone_view.toLocalizedTime(self.context.EffectiveDate())
        url = self.context.absolute_url()
        date = plone_view.toLocalizedTime(DateTime())
        loc = self.context.getLocation()
        loc = re.sub(' [0-9]{5}, ', ' ', loc)
        if self.context.getEXIF():
            the_date = DateTime(self.context.getEXIFOrigDate()).fCommon()
        else:
            the_date = DateTime(self.context.getEffectiveDate()).fCommon()
        the_date = the_date.split(' ')
        the_date = the_date[:-2] + ['at'] + the_date[-2:]
        the_date = ' '.join(the_date)
        # the_date = plone_view.toLocalizedTime(DateTime())

        
        if creator:
            prompt_text = translate(
                _(u'"%s" by %s. note taken on %s %s. Retrieved %s from %s. See original for copyright and licensing information.'),
                domain="ContentLicensing",
                target_language=self.request.LANGUAGE,
            ) % (
                safe_unicode(title),
                safe_unicode(creator),
                safe_unicode(the_date),
                safe_unicode(loc),
                safe_unicode(date),
                safe_unicode(url)
            )
        else:
            prompt_text = translate(
                _(u'"%s" on %s %s. Retrieved %s from %s. See original for copyright and licensing information.'),
                domain="ContentLicensing",
                target_language=self.request.LANGUAGE,
            ) % (
                safe_unicode(title),
                safe_unicode(the_date),
                safe_unicode(loc),
                safe_unicode(date),
                safe_unicode(url)
            )

        return prompt_text.replace('"','\\x22')
