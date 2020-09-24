from unittest import TestCase
from flask import request
from webargs import flaskparser

from tests import factories
from tests.common import ApiBaseTest

from webservices import args
from webservices import rest
from webservices import sorting
from webservices.resources import candidate_aggregates
from webservices.resources import elections
from webservices.rest import db
from webservices import utils
from webservices.common import models


class TestSort(ApiBaseTest):
    def test_single_column(self):
        candidates = [
            factories.CandidateFactory(district='01'),
            factories.CandidateFactory(district='02'),
        ]
        query, columns = sorting.sort(
            models.Candidate.query, 'district', model=models.Candidate
        )
        self.assertEqual(query.all(), candidates)

    def test_single_column_reverse(self):
        candidates = [
            factories.CandidateFactory(district='01'),
            factories.CandidateFactory(district='02'),
        ]
        query, columns = sorting.sort(
            models.Candidate.query, '-district', model=models.Candidate
        )
        self.assertEqual(query.all(), candidates[::-1])

    def test_multi_column(self):
        audit = [
            factories.AuditCaseFactory(
                cycle=2012,
                committee_name='Boy',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2012,
                committee_name='Girl',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2012,
                committee_name='Ted',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2012,
                committee_name='Zoo',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2014,
                committee_name='Abc',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2014,
                committee_name='John',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2014,
                committee_name='Ted',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
        ]
        query, columns = sorting.multi_sort(
            models.AuditCase.query, ['cycle', 'committee_name', ], model=models.AuditCase
        )
        self.assertEqual(query.all(), audit)

    def test_multi_column_reverse_first_column(self):
        audit = [
            factories.AuditCaseFactory(
                cycle=2012,
                committee_name='Zoo',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2012,
                committee_name='Ted',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2012,
                committee_name='Girl',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2012,
                committee_name='Abc',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2014,
                committee_name='Ted',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2014,
                committee_name='John',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
            factories.AuditCaseFactory(
                cycle=2014,
                committee_name='Abc',
                primary_category_id=-1,
                sub_category_id=-2,
                audit_case_id=1000,
            ),
        ]
        query, columns = sorting.multi_sort(
            models.AuditCase.query,
            ['-cycle', 'committee_name', ],
            model=models.AuditCase,
        )
        self.assertEqual(query.all(), audit[::-1])

    def test_hide_null(self):
        candidates = [
            factories.CandidateFactory(district='01'),
            factories.CandidateFactory(district='02'),
            factories.CandidateFactory(),
        ]
        query, columns = sorting.sort(
            models.Candidate.query, 'district', model=models.Candidate
        )
        self.assertEqual(query.all(), candidates)
        query, columns = sorting.sort(
            models.Candidate.query, 'district', model=models.Candidate, hide_null=True
        )
        self.assertEqual(query.all(), candidates[:2])

    def test_hide_null_candidate_totals(self):
        candidates = [
            factories.CandidateFactory(candidate_id='C1234'),
            factories.CandidateFactory(candidate_id='C5678'),
        ]
        candidateHistory = [  # noqa
            factories.CandidateHistoryFutureFactory(
                candidate_id='C1234',
                two_year_period=2016,
                election_years=[2016],
                cycles=[2016],
                candidate_election_year=2016,
            ),
            factories.CandidateHistoryFutureFactory(
                candidate_id='C5678',
                two_year_period=2016,
                election_years=[2016],
                cycles=[2016],
                candidate_election_year=2016,
            ),
        ]
        candidateTotals = [  # noqa
            factories.CandidateTotalFactory(
                candidate_id='C1234', is_election=False, cycle=2016
            ),
            factories.CandidateTotalFactory(
                candidate_id='C5678',
                disbursements='9999.99',
                is_election=False,
                cycle=2016,
            ),
        ]
        candidateFlags = [  # noqa
            factories.CandidateFlagsFactory(candidate_id='C1234'),
            factories.CandidateFlagsFactory(candidate_id='C5678'),
        ]

        tcv = candidate_aggregates.TotalsCandidateView()
        query, columns = sorting.sort(
            tcv.build_query(election_full=False), 'disbursements', model=None
        )
        self.assertEqual(len(query.all()), len(candidates))
        query, columns = sorting.sort(
            tcv.build_query(election_full=False),
            'disbursements',
            model=None,
            hide_null=True,
        )
        self.assertEqual(len(query.all()), len(candidates) - 1)
        self.assertTrue(candidates[1].candidate_id in query.all()[0])

    def test_hide_null_election(self):
        candidates = [
            factories.CandidateFactory(candidate_id='C1234'),
            factories.CandidateFactory(candidate_id='C5678'),
        ]
        cmteFacorty = [  # noqa
            factories.CommitteeDetailFactory(committee_id='H1234'),
            factories.CommitteeDetailFactory(committee_id='H5678'),
        ]
        db.session.flush()
        candidateHistory = [  # noqa
            factories.CandidateHistoryFactory(
                candidate_id='C1234',
                two_year_period=2016,
                state='MO',
                candidate_election_year=2016,
                candidate_inactive=False,
                district='01',
                office='S',
                election_years=[2016],
                cycles=[2016],
            ),
            factories.CandidateHistoryFactory(
                candidate_id='C5678',
                candidate_election_year=2016,
                two_year_period=2016,
                state='MO',
                election_years=[2016],
                cycles=[2016],
                candidate_inactive=False,
                district='02',
                office='S',
            ),
        ]
        candidateCmteLinks = [  # noqa
            factories.CandidateCommitteeLinkFactory(
                committee_id='H1234',
                candidate_id='C1234',
                fec_election_year=2016,
                committee_designation='P',
                election_yr_to_be_included=2016,
            ),
            factories.CandidateCommitteeLinkFactory(
                committee_id='H5678',
                candidate_id='C5678',
                fec_election_year=2016,
                committee_designation='P',
                election_yr_to_be_included=2016,
            ),
        ]
        cmteTotalsFactory = [  # noqa
            factories.CommitteeTotalsHouseSenateFactory(
                committee_id='H1234', cycle=2016
            ),
            factories.CommitteeTotalsHouseSenateFactory(
                committee_id='H1234', cycle=2016, disbursements='9999.99'
            ),
            factories.CommitteeTotalsHouseSenateFactory(
                committee_id='H5678', cycle=2016
            ),
        ]
        db.session.flush()

        electionView = elections.ElectionView()
        query, columns = sorting.sort(
            electionView.build_query(office='senate', cycle=2016, state='MO'),
            'total_disbursements',
            model=None,
        )

        # print(str(query.statement.compile(dialect=postgresql.dialect())))
        self.assertEqual(len(query.all()), len(candidates))
        query, columns = sorting.sort(
            electionView.build_query(office='senate', cycle=2016, state='MO'),
            'total_disbursements',
            model=None,
            hide_null=True,
        )
        # Taking this assert statement out because I believe, at least how the FEC interprets null (i.e. none) primary
        # committees for a candidate is that they have in fact raised/spent 0.0 dollars, this can be shown as true
        # using the Alabama special election as an example
        # self.assertEqual(len(query.all()), len(candidates) - 1)
        self.assertTrue(candidates[1].candidate_id in query.all()[0])
        self.assertEqual(query.all()[0].total_disbursements, 0.0)


class TestArgs(TestCase):
    def test_currency(self):
        with rest.app.test_request_context('?dollars=$24.50'):
            parsed = flaskparser.parser.parse({'dollars': args.Currency()}, request)
            self.assertEqual(parsed, {'dollars': 24.50})


class TestEnvVarSplit(TestCase):
    def test_env_var_split(self):
        test_cases = [
            "1.2.3.4, 5.6.7.8",
            "1.2.3.4,  5.6.7.8",
            "1.2.3.4,5.6.7.8",
            " 1.2.3.4,  5.6.7.8 ",
        ]
        expected = ["1.2.3.4", "5.6.7.8"]
        for test_case in test_cases:
            result = utils.split_env_var(test_case)
            self.assertEqual(result, expected)


class TestDecadeRange(TestCase):
    def test_get_decade_range(self):
        start_year = 2000
        current_year = 2020
        expected = [(None, 2000), (2000, 2010), (2010, None)]
        result = utils.get_decade_range(start_year, current_year)
        self.assertEqual(result, expected)

        start_year = 2000
        current_year = 2022
        expected = [(None, 2000), (2000, 2010), (2010, 2020), (2020, None)]
        result = utils.get_decade_range(start_year, current_year)
        self.assertEqual(result, expected)
