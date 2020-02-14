import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import { Header, Icon, Popup, Message } from 'semantic-ui-react'

import AwesomeBar from 'shared/components/page/AwesomeBar'
import DataLoader from 'shared/components/DataLoader'
import { InlineHeader, ButtonLink } from 'shared/components/StyledComponents'
import { VerticalSpacer } from 'shared/components/Spacers'
import { isActiveVariantSample } from 'shared/utils/constants'

const ProjectFilterContent = ({ project, removeField, projectSamples, value, dispatch, filterInputComponent, ...props }) => {
  let filterInput
  if (Object.values(projectSamples || {}).some(sample => isActiveVariantSample(sample))) {
    filterInput = filterInputComponent ? React.createElement(filterInputComponent, { ...props, value }) : null
  } else {
    filterInput = <Message
      color="red"
      header="Search is not enabled for this project"
      content="Please contact the seqr team to add this functionality"
    />
  }
  return (
    <div>
      <Header>
        <Popup
          trigger={<ButtonLink onClick={removeField}><Icon name="remove" color="grey" /></ButtonLink>}
          content="Remove this project from search"
        />
        Project: <Link to={`/project/${project.projectGuid}/project_page`}>{project.name}</Link>
      </Header>
      {filterInput}
      <VerticalSpacer height={10} />
    </div>
  )
}

ProjectFilterContent.propTypes = {
  project: PropTypes.object,
  value: PropTypes.object,
  removeField: PropTypes.func,
  projectSamples: PropTypes.object,
  dispatch: PropTypes.func,
  filterInputComponent: PropTypes.node,
}


export const ProjectFilter = ({ loading, load, ...props }) =>
  <DataLoader contentId={props.value} loading={loading} load={load} content={props.project} hideError>
    <ProjectFilterContent {...props} />
  </DataLoader>

ProjectFilter.propTypes = {
  project: PropTypes.object,
  value: PropTypes.object,
  load: PropTypes.func,
  loading: PropTypes.bool,
}

const PROJECT_SEARCH_CATEGORIES = ['projects']
const PROJECT_GROUP_SEARCH_CATEGORIES = ['project_groups']

export const AddProjectButton = ({ addElement, addProjectGroup, processAddedElement }) =>
  <div>
    <InlineHeader content="Add Project:" />
    <AwesomeBar
      categories={PROJECT_SEARCH_CATEGORIES}
      placeholder="Search for a project"
      inputwidth="400px"
      onResultSelect={result => addElement(processAddedElement ? processAddedElement(result) : result.key)}
    />
    <InlineHeader content="Add Project Group:" />
    <AwesomeBar
      categories={PROJECT_GROUP_SEARCH_CATEGORIES}
      placeholder="Search for a project group"
      inputwidth="400px"
      onResultSelect={result => addProjectGroup(result.key, addElement)}
    />
  </div>

AddProjectButton.propTypes = {
  addElement: PropTypes.func,
  addProjectGroup: PropTypes.func,
  processAddedElement: PropTypes.func,
}