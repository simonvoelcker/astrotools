import React, { Component } from 'react'
import { ListGroupItem } from 'reactstrap'
import { AppContext } from '../../context/AppContext'
import JobInfoModal from '../modals/JobInfoModal'
import DeleteJobModal from '../modals/DeleteJobModal'
import { getGcodeFile, jobIsStarted } from '../../Utils'
import PropTypes from 'prop-types'
import { SortableHandle } from 'react-sortable-hoc'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faInfoCircle, faTrashAlt, faPlay, faCogs, faBars, faNetworkWired } from '@fortawesome/free-solid-svg-icons'

library.add(faInfoCircle, faTrashAlt, faPlay, faCogs, faBars, faNetworkWired)

const DragHandle = SortableHandle(() => <FontAwesomeIcon icon='bars' />)

export default class JobListItem extends Component {
  // We need to keep track of the mounting-state, because it can happen that a JobListItem is
  // unmounted and then tries to hide its own confirmation dialog.
  // The underlying reason lies in the fact that the dialog is part of the JobListItem.
  _isMounted = false;

  constructor (props) {
    super(props)

    this.state = {
      showSuccessMessage: false,
      showInfoModal: false,
      showRemoveModal: false
    }
  }

  componentDidMount () {
    this._isMounted = true
  }

  componentWillUnmount () {
    this._isMounted = false
  }

  showRemoveModal = () => {
    this.setState({ showRemoveModal: true })
  }

  hideRemoveModal = () => {
    if (this._isMounted) {
      this.setState({ showRemoveModal: false })
    }
  }

  removeJob = (filename, jobId) => {
    this.context.mutations.removeJob(jobId).then(() => {
      this.context.mutations.updateFileList()

      let message = 'job '.concat(filename.split('.')[0], ' was removed from the printer')
      this.context.mutations.logMessage(message)

      this.hideRemoveModal()
    })
  }

  showInfoModal = () => {
    this.setState({ showInfoModal: true })
  }

  hideInfoModal = () => {
    this.setState({ showInfoModal: false })
  }

  render () {
    const name = this.props.job.name
    const { showInfoModal, showRemoveModal } = this.state

    const jobID = this.props.job._id
    const gcodeFile = getGcodeFile(this.props.job)
    const isStarted = this.context.store.printingNow && jobIsStarted(this.props.job)
    const printProgress = Math.min(100, Math.round(this.props.printProgress * 100))
    const display = this.props.display

    return (
      <div>
        <ListGroupItem
          data-cy='ListItem'
          className={gcodeFile ? (isStarted ? 'started-job-item' : 'job-item') : 'update-job-item'}>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>

            <h2 style={{ margin: '0', display: 'flex' }}>

              {isStarted ? <FontAwesomeIcon icon='play' /> : <DragHandle />}

              { display &&
                <div style={{ marginLeft: '15px' }}>
                  {gcodeFile ? (
                    <FontAwesomeIcon data-cy='InfoButton' icon='info-circle' onClick={this.showInfoModal} />
                  ) : (
                    <FontAwesomeIcon icon='cogs' />
                  )}
                </div>
              }

              {display ?
                <span style={{ width: '800px' }}>{isStarted
                  ? <span className='file_list_text'>{name} ({printProgress}%)</span>
                  : <span className='file_list_text'>{name}</span>
                }</span>
              :
                <span style={{ width: '800px' }}>{isStarted
                  ? <span className='file_list_text' style={{ 'marginLeft': '20px' }}>{name} ({printProgress}%)</span>
                  : <span className='file_list_text' style={{ 'marginLeft': '20px' }}>{name}</span>
                }</span>
              }
            </h2>

            {!isStarted && this.context.store.mode !== 'demo' &&
            <h2 style={{ margin: '0' }}>
              <FontAwesomeIcon data-cy='DeleteButton' icon='trash-alt' onClick={this.showRemoveModal} />
            </h2>
            }
          </div>

          <DeleteJobModal
            isOpen={showRemoveModal}
            toggle={this.hideRemoveModal}
            jobId={jobID}
            filename={gcodeFile != null ? gcodeFile.filename : name}
            removeJob={this.removeJob}
          />

          {gcodeFile != null && showInfoModal && (
            <JobInfoModal gcodeFile={gcodeFile} isOpen={showInfoModal} toggle={this.hideInfoModal} />
          )}
        </ListGroupItem>
      </div>
    )
  }
}

JobListItem.contextType = AppContext

JobListItem.propTypes = {
  job: PropTypes.object,
  display: PropTypes.bool
}
