import React from 'react'
import PropTypes from 'prop-types'

import { connect } from 'react-redux'
import { Grid } from 'semantic-ui-react'
import Timeago from 'timeago.js'

import PedigreeIcon from 'shared/components/icons/PedigreeIcon'
import TextFieldView from 'shared/components/panel/view-fields/TextFieldView'
import PhenotipsDataPanel from 'shared/components/panel/view-phenotips-info/PhenotipsDataPanel'
import { getProject, updateIndividual } from 'redux/rootReducer'

import CaseReviewStatusDropdown from './CaseReviewStatusDropdown'
import { getShowDetails } from '../../../../Project/reducers'

const detailsStyle = {
  padding: '5px 0 5px 5px',
  fontSize: '11px',
  fontWeight: '500',
  color: '#999999',
}

class IndividualRow extends React.Component
{
  static propTypes = {
    project: PropTypes.object.isRequired,
    family: PropTypes.object.isRequired,
    individual: PropTypes.object.isRequired,
    showDetails: PropTypes.bool.isRequired,
    updateIndividual: PropTypes.func,
  }

  render() {
    const { project, family, individual, showDetails } = this.props

    const { individualId, displayName, paternalId, maternalId, sex, affected, createdDate } = individual

    return (
      <Grid stackable style={{ width: '100%' }}>
        <Grid.Row style={{ padding: '0px' }}>
          <Grid.Column width={3} style={{ maxWidth: '250px', padding: '0px 0px 15px 15px' }}>
            <span>
              <div style={{ display: 'block', verticalAlign: 'top', whiteSpace: 'nowrap' }} >
                <PedigreeIcon style={{ fontSize: '13px' }} sex={sex} affected={affected} />
                &nbsp;
                {displayName || individualId}
              </div>
              <div style={{ display: 'block' }} >
                {
                  (!family.pedigreeImage && ((paternalId && paternalId !== '.') || (maternalId && maternalId !== '.'))) ? (
                    <div style={detailsStyle}>
                      child of &nbsp;
                      <i>{(paternalId && maternalId) ? `${paternalId} and ${maternalId}` : (paternalId || maternalId) }</i>
                      <br />
                    </div>
                  ) : null
                }
                {
                  showDetails ? (
                    <div style={detailsStyle}>
                      ADDED {new Timeago().format(createdDate).toUpperCase()}
                    </div>
                    ) : null
                }
              </div>
            </span>
          </Grid.Column>
          <Grid.Column width={10} style={{ maxWidth: '950px' }}>
            {
              showDetails ?
                (individual.notes || individual.caseReviewDiscussion) &&
                <div style={{ padding: '0px 0px 10px 0px' }}>
                  {
                    <TextFieldView
                      isVisible={individual.caseReviewDiscussion}
                      isEditable
                      fieldName="Case Review Discussion"
                      fieldId="caseReviewDiscussion"
                      initialText={individual.caseReviewDiscussion}
                      textEditorId={`editCaseReviewDiscussion-${individual.individualGuid}`}
                      textEditorTitle={`Case Review Discussion for Individual ${individual.individualId}`}
                      textEditorSubmit={this.props.updateIndividual}
                    />
                  }
                  {
                    <TextFieldView
                      isVisible={individual.notes}
                      isEditable
                      fieldName="Individual Notes"
                      fieldId="notes"
                      initialText={individual.notes}
                      textEditorId={`editNotes-${individual.individualGuid}`}
                      textEditorTitle={`Notes for Individual ${individual.individualId}`}
                      textEditorSubmitUrl={`/api/individual/${individual.individualGuid}/update/notes`}
                      textEditorSubmit={this.props.updateIndividual}
                    />
                  }
                </div>
                : null
            }
            <PhenotipsDataPanel project={project} individual={individual} showDetails={showDetails} showEditPhenotipsLink={false} />
          </Grid.Column>
          <Grid.Column width={3} style={{ paddingRight: '0px' }}>
            <div style={{ float: 'right', width: '220px' }}>
              <CaseReviewStatusDropdown individual={individual} />
              {
                showDetails && individual.caseReviewStatusLastModifiedDate ? (
                  <div style={{ ...detailsStyle, marginLeft: '2px' }}>
                    CHANGED {new Timeago().format(individual.caseReviewStatusLastModifiedDate).toUpperCase()}
                    { individual.caseReviewStatusLastModifiedBy && ` BY ${individual.caseReviewStatusLastModifiedBy}` }
                  </div>
                ) : null
              }
            </div>
          </Grid.Column>
        </Grid.Row>
      </Grid>)
  }
}

export { IndividualRow as IndividualRowComponent }

const mapStateToProps = state => ({
  project: getProject(state),
  showDetails: getShowDetails(state),
})


const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    updateIndividual: (values) => {
      dispatch(updateIndividual(ownProps.individual.individualGuid, values))
    },
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(IndividualRow)
