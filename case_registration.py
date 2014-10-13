from openerp.osv import osv, fields
from tools.translate import _
import addons.decimal_precision as dp
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date
import openerp.exceptions
import time

class case_registration(osv.osv):
    _name = 'case.registration'
    _order = "id desc"
    
    def create(self, cr, uid, data, context=None):
        data['state'] = 'filed'
        return super(case_registration, self).create(cr, uid, data, context=context)
    
    def action_dismiss(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'state':'dismissed'})
        return False
    
    def action_close(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'state':'closed'})
        return False
    
    def _deflt_ass_year(self, cr, uid, ids, context=None):
        today = date.today()
        month_of = today.month
        if month_of <= 3:
            date_of = '%d-%d'%(today.year-1,today.year)
        if month_of >= 4:
            date_of = '%d-%d'%(today.year,today.year+1)
        company_id = self.pool['res.company']._company_default_get(cr,uid,object='case.registration'),
        search_condition = [('name', '=', date_of),('company_id','=',company_id)]
        search_ids = self.pool.get('account.fiscalyear').search(cr, uid, search_condition, context=context)
        if search_ids:
            similar_objs = self.pool.get('account.fiscalyear').browse(cr, uid, search_ids, context=context)
        if similar_objs:
            return similar_objs[0].id
        return False
    def on_change_wakf_regno_to_name(self, cr, uid, ids, reg_no, context=None):
        values = {}
        if reg_no:
            id_res_partner=self.pool.get('res.partner')
            search_condition = [('wakf_reg_no', '=', reg_no)]
            search_ids = id_res_partner.search(cr, uid, search_condition, context=context)
            if search_ids:
                similar_objs = id_res_partner.browse(cr, uid, search_ids, context=context)[0]
                values={'wakf_name':similar_objs.id,
                        'wakf_district':similar_objs.district_id.id,
                        'wakf_taluk':similar_objs.taluk_id.id,
                        'wakf_village':similar_objs.village_id.id,
                        'wakf_address':similar_objs.wakf_management_id[0].details_waquif,
                        }
            else:
                values={'wakf_name':False,
                        'wakf_district':False,
                        'wakf_taluk':False,
                        'wakf_village':False,
                        'wakf_address':False,
                        }
        return {'value' :values}
    
    _columns = {
        'case_no': fields.char('Case No'),
        'case_type': fields.selection([
                    ('aa', 'AA'),
                    ('ep', 'EP'),
                    ('op', 'OP'),            
                    ('coveat', 'Coveat'),
                    ('misc', 'Misc.'),
                    ],'Case Type', readonly=False),
        'case_year': fields.date('Date of Registration'),
        'section_id': fields.many2one('case.section','Under Section',ondelete="set null"),
        'condition_id': fields.many2one('present.condition','Present Condition',ondelete="set null"),
        'wakf_reg_no': fields.integer('Wakf register No'),
        'wakf_name': fields.many2one('res.partner','Wakf Name',ondelete="set null"),
        'wakf_district': fields.many2one('wakf.district','District',ondelete="set null"),
        'wakf_taluk': fields.many2one('wakf.taluk','Taluk',ondelete="set null"),
        'wakf_village': fields.many2one('wakf.village','Village',ondelete="set null"),
        'wakf_address': fields.text('Wakf Address'),
        'assess_year': fields.many2one('account.fiscalyear','Assessment Year',ondelete="set null"),
        'board_meeting_date': fields.datetime('Board Meeting Date'),
        'id_proceedings': fields.one2many('proceedings.details','id_proceedings'),
        'id_petitioner': fields.one2many('case.petitioner','id_petitioner'),
        'id_respondent': fields.one2many('case.respondent','id_respondent'),
        'id_ia': fields.one2many('idakkala.adalath','ia_id'),
        'company_id': fields.many2one('res.company','Company'),
        'state': fields.selection([
                    ('filed', 'Filed'),
                    ('proceeding', 'Proceeding'),
                    ('dismissed', 'Dismissed'),            
                    ('closed', 'Closed'),
                    ],'States', readonly=False),
        'dispose': fields.selection([
                    ('bundle_no', 'Disposed Bundle Number'),
                    ('abeyance', 'Kept in Abeyance Number'),
                    ('defective', 'Defective Bundle Number'),            
                    ],'Dispose Status', readonly=False),
        'number': fields.char('Number'),
        'delay_calender': fields.float('Board Meeting Duration (In Hr.)'),
        }
    _defaults = {
        'company_id': lambda self,cr,uid,ctx: self.pool['res.company']._company_default_get(cr,uid,object='case.registration',context=ctx),
        'assess_year': _deflt_ass_year,
        'case_year': lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),             
                 }
case_registration()

class case_section(osv.osv):
    _name = 'case.section'
    _columns = {
        'under_section': fields.char('Under Section'),
        'section_details': fields.text('Section Details'),
                }
case_section()

class present_condition(osv.osv):
    _name = 'present.condition'
    _columns = {
        'name': fields.char('Condition'),
        'condition_overview': fields.text('Condition Overview'),
                }
present_condition()

class advocate_master(osv.osv):
    _name = 'advocate.master'
    _columns = {
        'name': fields.char('Advocate Name'),
        'address': fields.text('Address'),
        'mobile_no': fields.char('Mobile No'),
        'office_no': fields.char('Office No'),
                }
advocate_master()

###############################################################################################################################
####################################################  PETITIONER DETAILS ######################################################
###############################################################################################################################

class petitioner_details(osv.osv):
    _name = 'case.petitioner'
        
    def on_change_advocate_to_address(self, cr, uid, ids, advocate, context=None):
        values = {}
        if advocate:
            advocate_address = self.pool.get('advocate.master').browse(cr,uid,advocate).address
            if advocate_address:
                values = {'advocate_address':advocate_address}
            else:
                values = {'advocate_address':False}
        return {'value':values}
    
    _columns = {
        'name': fields.char('Petitioner Name'),
        'petitioner_address': fields.text('Address'),
        'advocate_name': fields.many2one('advocate.master','Advocate'),
        'advocate_address': fields.text('Address',readonly=True),
        'id_petitioner': fields.many2one('case.registration','Petitioner Details',ondelete="set null"),
        'petitioner_id': fields.many2one('idakkala.adalath','Petitioner Details',ondelete="set null")
                }
petitioner_details()

###############################################################################################################################
####################################################  RESPONDENT DETAILS ######################################################
###############################################################################################################################

class respondent_details(osv.osv):
    _name = 'case.respondent'
    
    def on_change_advocate_to_address(self, cr, uid, ids, advocate, context=None):
        values = {}
        if advocate:
            advocate_address = self.pool.get('advocate.master').browse(cr,uid,advocate).address
            if advocate_address:
                values = {'advocate_address':advocate_address}
            else:
                values = {'advocate_address':False}
        return {'value':values}
    
    _columns = {
        'name': fields.char('Respondent Name'),
        'respondent_address': fields.text('Address'),
        'advocate_name': fields.many2one('advocate.master','Advocate'),
        'advocate_address': fields.text('Address',readonly=True),
        'id_respondent': fields.many2one('case.registration','Respondent Details',ondelete="set null"),
        'respondent_id': fields.many2one('idakkala.adalath','Respondent Details',ondelete="set null")
                }
respondent_details()

###############################################################################################################################
####################################################  PROCEEDINGS DETAILS ######################################################
###############################################################################################################################
class proceedings_details(osv.osv):
    _name = 'proceedings.details'
    _order = "id desc"
    _columns = {
        'board_date': fields.date('Board Meeting Date'),
        'order_details': fields.text('Order Details'),
        'condition_id': fields.many2one('present.condition','Present Condition',ondelete="set null"),
        'id_proceedings': fields.many2one('case.registration','Proceedings Details',ondelete="set null")
                }
proceedings_details()


###############################################################################################################################
####################################################  IA DETAILS ##############################################################
###############################################################################################################################

class IA_details(osv.osv):
    _name = 'idakkala.adalath'
    _order = "id desc"
    _columns = {
        'ia_no': fields.char('IA Number'),
        'ia_filed_on': fields.date('IA Filed On'),
        'ia_purpose': fields.many2one('ia.purpose','IA Purpose',ondelete="set null"),
        'ia_by': fields.many2one('advocate.master','IA By Whom',ondelete="set null"),
        'ia_id': fields.many2one('case.registration','IA Details',ondelete="set null"),
        'condition_id1': fields.many2one('present.condition','Present Condition',ondelete="set null"),
        'proceedings_ia_id': fields.one2many('ia.proceedings','proceeings_id'),
        'petitioner_ia_id': fields.one2many('case.petitioner','petitioner_id'),
        'respondent_ia_id': fields.one2many('case.respondent','respondent_id'),

                }
IA_details()

class IA_purpose(osv.osv):
    _name = 'ia.purpose'
    _columns = {
        'name': fields.char('Purpose Name'),
        'details': fields.text('Purpose Details'),
                }
IA_purpose()

class IA_proceedings_details(osv.osv):
    _name = 'ia.proceedings'
    _columns = {
        'board_date': fields.date('Board Meeting Date'),
        'order_details': fields.text('Order Details'),
        'condition_id': fields.many2one('present.condition','Present Condition',ondelete="set null"),
        'proceeings_id': fields.many2one('idakkala.adalath','Proceedings Details',ondelete="set null")
                }
IA_proceedings_details()