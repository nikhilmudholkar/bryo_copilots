import pandas
from odoo import api, fields, models, tools

class CopilotSuggestionsView(models.Model):
    _name = "copilot.suggestions.view"
    _auto = False
    _description = "AI copilot suggestions view"
    sales_order_id = fields.Char(string='Sales Order')
    recommendation = fields.Char(string='Recommendation')
    recommendation_time = fields.Datetime(string='Recommendation Time')

    @api.model
    def init(self):
        if tools.table_exists(self._cr, "copilot_suggestions"):
            # print("table copilot_suggestions_view exists")
            self._cr.execute("""DROP TABLE copilot_suggestions CASCADE""")
            # print("table copilot_suggestions_view dropped")
        # create table copilot_suggestions_view
        self._cr.execute("""CREATE TABLE copilot_suggestions (
                    id serial NOT NULL,
                    sales_order_id varchar,
                    recommendation varchar,
                    recommendation_time varchar
                    )""")
        tools.drop_view_if_exists(self._cr, 'copilot_suggestions')
        # check if table copilot_suggestions exists
        # if tools.table_exists("copilot_suggestions"):
        self._cr.execute("""CREATE OR REPLACE VIEW copilot_suggestions_view AS (
                    SELECT row_number() OVER () as id,
                    sales_order_id,
                    recommendation,
                    recommendation_time
                    FROM copilot_suggestions)""")



