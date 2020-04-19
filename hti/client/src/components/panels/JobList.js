import React, { Component } from 'react'
import { ListGroup } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { SortableList } from '../../components/panels/SortableList'
import DragAndDrop from '../../components/panels/DragAndDrop'
import PropTypes from 'prop-types'

export default class JobList extends Component {
  constructor (props) {
    super(props)
    this.state = {
      showSuccessMessage: false,
      uploadPercentage: -1
    }
    this.scene = props.scene
    this.JOB_UPLOAD_STARTED = 'A job upload to the printer has been started'
    this.JOB_UPLOAD_SUCCESS = 'A new job was successfully uploaded to the printer'
    this.JOB_UPLOAD_FAILED = 'There was a problem uploading the job to the printer. Error: '
  }

  handleUploadSuccess = () => {
    this.context.mutations.setUploadPercentage(-1)
    this.context.mutations.logMessage(this.JOB_UPLOAD_SUCCESS)
  }

  showUploadPercentage = () => {
    this.context.mutations.setUploadPercentage(0)
  }

  handleDrop = (files) => {
    if (files.length === 1) {
      const fileName = files[0].name
      this.context.mutations.setUploadFilename(fileName)

      this.showUploadPercentage()
      this.submitFile(files[0])
    }
  }

  submitFile = (file) => {
    if (!file) return

    this.context.mutations.logMessage(this.JOB_UPLOAD_STARTED)
    // Initialize the form data
    let formData = new FormData()
    // Add the form data we need to submit
    formData.append('file', file)

    let configData = {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        let uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        this.context.mutations.setUploadPercentage(parseInt(uploadProgress, 10))
      }
    }

    this.context.mutations.uploadFile(formData, configData, () => {
      this.handleUploadSuccess()
    }, () => {
      this.context.mutations.setUploadPercentage(-1)
      this.context.mutations.logMessage(this.JOB_UPLOAD_FAILED)
    })
  }

  render () {
    const isInfoPage = this.scene === 'SceneInfos'
    const isUploading = (this.context.store.uploadPercentage > -1 && this.context.store.uploadPercentage <= 100)
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div>
            {
              isInfoPage ? (
                store.jobQueue[0] || isUploading ? (
                  <div data-cy='JobList'>
                    <p style={{ margin: '20px 0 0 0', fontSize: '12px' }}>
                      Job Management @ {
                        store.machineInfo
                          ? ( store.machineInfo.hmiEnvironment.hostName ? 'http://' + store.machineInfo.hmiEnvironment.hostName + ':5000/manage' : 'Network not available')
                          : 'Cannot retrieve URL'
                      }
                    </p>
                    <ListGroup className='panel-scroll' style={{ width: '885px', height: '330px' }} >
                      <SortableList useDragHandle scene={this.scene} printProgress={store.printProgress} items={store.jobQueue} onSortEnd={mutations.moveJob} />
                    </ListGroup>
                  </div>
                ) : (
                  <h1 style={{ textAlign: 'center' }}>NO JOBS</h1>
                )
              ) : (
                store.jobQueue[0] || isUploading ? (
                  <div style={{ marginTop: '2rem' }} data-cy='JobList'>
                    <ListGroup className='panel-scroll'>
                      <DragAndDrop handleDrop={this.handleDrop}>
                        <div style={{ width: '930px', height: '530px' }}>
                          <SortableList useDragHandle scene={this.scene} printProgress={store.printProgress} items={store.jobQueue} onSortEnd={mutations.moveJob} />
                        </div>
                      </DragAndDrop>
                    </ListGroup>
                  </div>
                ) : (
                  <div style={{ marginTop: '2rem' }} data-cy='JobList'>
                    <ListGroup className='panel-scroll'>
                      <DragAndDrop handleDrop={this.handleDrop}>
                        <h1 style={{ width: '930px', height: '500px', textAlign: 'center' }}>NO JOBS</h1>
                      </DragAndDrop>
                    </ListGroup>
                  </div>
                )
              )
            }
          </div>
        )}
      </AppConsumer>
    )
  }
}

JobList.contextType = AppContext

JobList.propTypes = {
  scene: PropTypes.string
}
