"""
APIs used to retrieve and modify Individual fields
"""
import json

from django.contrib.auth.models import User
from matchmaker.models import MatchmakerSubmission
from seqr.views.utils.file_utils import save_uploaded_file, load_uploaded_file
from seqr.views.utils.individual_utils import delete_individuals
from seqr.views.utils.json_to_orm_utils import update_family_from_json, update_model_from_json, \
    get_or_create_model_from_json, create_model_from_json
from seqr.views.utils.json_utils import create_json_response
from seqr.views.utils.note_utils import create_note_handler, update_note_handler, delete_note_handler
from seqr.views.utils.orm_to_json_utils import _get_json_for_family, _get_json_for_individuals, \
    get_json_for_family_note, get_json_for_family_notes, get_json_for_samples, get_json_for_matchmaker_submissions
from seqr.views.utils.project_context_utils import add_child_ids, families_discovery_tags
from seqr.models import Family, FamilyAnalysedBy, Individual, FamilyNote, Sample, IgvSample
from seqr.views.utils.permissions_utils import check_project_permissions, get_project_and_check_pm_permissions, \
    login_and_policies_required, user_is_analyst, has_case_review_permissions


FAMILY_ID_FIELD = 'familyId'
PREVIOUS_FAMILY_ID_FIELD = 'previousFamilyId'


@login_and_policies_required
def family_page_data(request, family_guid):
    family = Family.objects.get(guid=family_guid)
    project = family.project
    check_project_permissions(project, request.user)
    is_analyst = user_is_analyst(request.user)
    has_case_review_perm = has_case_review_permissions(project, request.user)

    family_json = _get_json_for_family(
        family, request.user, project_guid=project.guid, is_analyst=is_analyst, has_case_review_perm=has_case_review_perm)
    response = families_discovery_tags([family_json])

    family_notes = get_json_for_family_notes(FamilyNote.objects.filter(family=family), is_analyst=is_analyst)

    individual_models = Individual.objects.filter(family=family)
    individuals = _get_json_for_individuals(
        individual_models, project_guid=project.guid, add_hpo_details=True, skip_nested=True,
        is_analyst=is_analyst, has_case_review_perm=has_case_review_perm)

    sample_models = Sample.objects.filter(individual__in=individual_models)
    samples = get_json_for_samples(sample_models, project_guid=project.guid, skip_nested=True, is_analyst=is_analyst)

    igv_sample_models = IgvSample.objects.filter(individual__in=individual_models)
    igv_samples = get_json_for_samples(
        igv_sample_models, project_guid=project.guid, skip_nested=True, is_analyst=is_analyst)

    submissions = get_json_for_matchmaker_submissions(MatchmakerSubmission.objects.filter(individual__family=family))
    individual_mme_submission_guids = {s['individualGuid']: s['submissionGuid'] for s in submissions}
    for individual in individuals:
        individual['mmeSubmissionGuid'] = individual_mme_submission_guids.get(individual['individualGuid'])

    response.update({
        'familyNotesByGuid': {n['noteGuid']: n for n in family_notes},
        'individualsByGuid': {i['individualGuid']: i for i in individuals},
        'igvSamplesByGuid': {s['sampleGuid']: s for s in igv_samples},
        'mmeSubmissionsByGuid': {s['submissionGuid']: s for s in submissions},
        'samplesByGuid': {s['sampleGuid']: s for s in samples},
    })
    add_child_ids(response, include_family_entities=True)

    return create_json_response(response)

@login_and_policies_required
def edit_families_handler(request, project_guid):
    """Edit or one or more Family records.

    Args:
        project_guid (string): GUID of project that contains these individuals.
    """

    project = get_project_and_check_pm_permissions(project_guid, request.user)

    request_json = json.loads(request.body)

    if request_json.get('uploadedFileId'):
        modified_families = load_uploaded_file(request_json.get('uploadedFileId'))
    else:
        modified_families = request_json.get('families')
    if modified_families is None:
        return create_json_response(
            {}, status=400, reason="'families' not specified")

    updated_families = []
    for fields in modified_families:
        if fields.get('familyGuid'):
            family = Family.objects.get(project=project, guid=fields['familyGuid'])
        elif fields.get(PREVIOUS_FAMILY_ID_FIELD):
            family = Family.objects.get(project=project, family_id=fields[PREVIOUS_FAMILY_ID_FIELD])
        else:
            family, _ = get_or_create_model_from_json(
                Family, {'project': project, 'family_id': fields[FAMILY_ID_FIELD]},
                update_json=None, user=request.user)

        update_family_from_json(family, fields, user=request.user, allow_unknown_keys=True)
        updated_families.append(family)

    updated_families_by_guid = {
        'familiesByGuid': {
            family.guid: _get_json_for_family(family, request.user, add_individual_guids_field=True) for family in updated_families
        }
    }

    return create_json_response(updated_families_by_guid)


@login_and_policies_required
def delete_families_handler(request, project_guid):
    """Edit or delete one or more Individual records.

    Args:
        project_guid (string): GUID of project that contains these individuals.
    """

    project = get_project_and_check_pm_permissions(project_guid, request.user)

    request_json = json.loads(request.body)

    families_to_delete = request_json.get('families')
    if families_to_delete is None:
        return create_json_response(
            {}, status=400, reason="'recordIdsToDelete' not specified")
    family_guids_to_delete = [f['familyGuid'] for f in families_to_delete]

    # delete individuals 1st
    individual_guids_to_delete = [i.guid for i in Individual.objects.filter(
        family__project=project, family__guid__in=family_guids_to_delete)]
    delete_individuals(project, individual_guids_to_delete, request.user)

    # delete families
    Family.bulk_delete(request.user, project=project, guid__in=family_guids_to_delete)

    # send response
    return create_json_response({
        'individualsByGuid': {
            individual_guid: None for individual_guid in individual_guids_to_delete
        },
        'familiesByGuid': {
            family_guid: None for family_guid in family_guids_to_delete
        },
    })


@login_and_policies_required
def update_family_fields_handler(request, family_guid):
    """Updates the specified field in the Family model.

    Args:
        family_guid (string): GUID of the family.
    """

    family = Family.objects.get(guid=family_guid)

    # check permission - can be edited by anyone with access to the project
    check_project_permissions(family.project, request.user)

    request_json = json.loads(request.body)
    update_family_from_json(family, request_json, user=request.user, allow_unknown_keys=True, immutable_keys=[
        'family_id', 'display_name',
    ])

    return create_json_response({
        family.guid: _get_json_for_family(family, request.user)
    })


@login_and_policies_required
def update_family_assigned_analyst(request, family_guid):
    """Updates the specified field in the Family model.

    Args:
        family_guid (string): GUID of the family.
    """
    family = Family.objects.get(guid=family_guid)
    # assigned_analyst can be edited by anyone with access to the project
    check_project_permissions(family.project, request.user, can_edit=False)

    request_json = json.loads(request.body)
    assigned_analyst_username = request_json.get('assigned_analyst_username')

    if assigned_analyst_username:
        try:
            assigned_analyst = User.objects.get(username=assigned_analyst_username)
        except Exception:
            return create_json_response(
                {}, status=400, reason="specified user does not exist")
    else:
        assigned_analyst = None
    update_model_from_json(family, {'assigned_analyst': assigned_analyst}, request.user)

    return create_json_response({
        family.guid: _get_json_for_family(family, request.user)
    })


@login_and_policies_required
def update_family_analysed_by(request, family_guid):
    """Updates the specified field in the Family model.

    Args:
        family_guid (string): GUID of the family.
        field_name (string): Family model field name to update
    """

    family = Family.objects.get(guid=family_guid)
    # analysed_by can be edited by anyone with access to the project
    check_project_permissions(family.project, request.user, can_edit=False)

    create_model_from_json(FamilyAnalysedBy, {'family': family}, request.user)

    return create_json_response({
        family.guid: _get_json_for_family(family, request.user)
    })


@login_and_policies_required
def update_family_pedigree_image(request, family_guid):
    """Updates the specified field in the Family model.

    Args:
        family_guid (string): GUID of the family.
    """

    family = Family.objects.get(guid=family_guid)

    # check permission
    check_project_permissions(family.project, request.user, can_edit=True)

    if len(request.FILES) == 0:
        pedigree_image = None
    elif len(request.FILES) > 1:
        return create_json_response({}, status=400, reason='Received {} files'.format(len(request.FILES)))
    else:
        pedigree_image = next(iter((request.FILES.values())))

    update_model_from_json(family, {'pedigree_image': pedigree_image}, request.user)

    return create_json_response({
        family.guid: _get_json_for_family(family, request.user)
    })


@login_and_policies_required
def receive_families_table_handler(request, project_guid):
    """Handler for the initial upload of an Excel or .tsv table of families. This handler
    parses the records, but doesn't save them in the database. Instead, it saves them to
    a temporary file and sends a 'uploadedFileId' representing this file back to the client.

    Args:
        request (object): Django request object
        project_guid (string): project GUID
    """

    project = get_project_and_check_pm_permissions(project_guid, request.user)

    def _process_records(records, filename=''):
        column_map = {}
        for i, field in enumerate(records[0]):
            key = field.lower()
            if 'family' in key:
                if 'prev' in key:
                    column_map[PREVIOUS_FAMILY_ID_FIELD] = i
                else:
                    column_map[FAMILY_ID_FIELD] = i
            elif 'display' in key:
                column_map['displayName'] = i
            elif 'description' in key:
                column_map['description'] = i
            elif 'phenotype' in key:
                column_map['codedPhenotype'] = i
        if FAMILY_ID_FIELD not in column_map:
            raise ValueError('Invalid header, missing family id column')

        return [{column: row[index] if isinstance(index, int) else next((row[i] for i in index if row[i]), None)
                for column, index in column_map.items()} for row in records[1:]]

    try:
        uploaded_file_id, filename, json_records = save_uploaded_file(request, process_records=_process_records)
    except Exception as e:
        return create_json_response({'errors': [str(e)], 'warnings': []}, status=400, reason=str(e))

    prev_fam_ids = {r[PREVIOUS_FAMILY_ID_FIELD] for r in json_records if r.get(PREVIOUS_FAMILY_ID_FIELD)}
    existing_prev_fam_ids = {f.family_id for f in Family.objects.filter(family_id__in=prev_fam_ids, project=project).only('family_id')}
    if len(prev_fam_ids) != len(existing_prev_fam_ids):
        missing_prev_ids = [family_id for family_id in prev_fam_ids if family_id not in existing_prev_fam_ids]
        return create_json_response(
            {'errors': [
                'Could not find families with the following previous IDs: {}'.format(', '.join(missing_prev_ids))
            ], 'warnings': []},
            status=400, reason='Invalid input')

    fam_ids = {r[FAMILY_ID_FIELD] for r in json_records if not r.get(PREVIOUS_FAMILY_ID_FIELD)}
    num_families_to_update = len(prev_fam_ids) + Family.objects.filter(family_id__in=fam_ids, project=project).count()

    num_families = len(json_records)
    num_families_to_create = num_families - num_families_to_update

    info = [
        "{num_families} families parsed from {filename}".format(num_families=num_families, filename=filename),
        "{} new families will be added, {} existing families will be updated".format(num_families_to_create, num_families_to_update),
    ]

    return create_json_response({
        'uploadedFileId': uploaded_file_id,
        'errors': [],
        'warnings': [],
        'info': info,
    })

@login_and_policies_required
def create_family_note(request, family_guid):
    family = Family.objects.get(guid=family_guid)
    check_project_permissions(family.project, request.user)

    return create_note_handler(
        request, FamilyNote, parent_fields={'family': family}, additional_note_fields=['noteType'],
        get_response_json=lambda note: {'familyNotesByGuid': {note.guid: get_json_for_family_note(note)}},
    )


@login_and_policies_required
def update_family_note(request, family_guid, note_guid):
    return update_note_handler(
        request, FamilyNote, family_guid, note_guid, parent_field='family__guid',
        get_response_json=lambda note: {'familyNotesByGuid': {note_guid: get_json_for_family_note(note)}},
    )


@login_and_policies_required
def delete_family_note(request, family_guid, note_guid):
    return delete_note_handler(
        request, FamilyNote, family_guid, note_guid, parent_field='family__guid',
        get_response_json=lambda: {'familyNotesByGuid': {note_guid: None}},
    )
