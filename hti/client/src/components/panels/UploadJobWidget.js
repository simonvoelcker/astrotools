import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { Col } from 'reactstrap'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFileUpload } from '@fortawesome/free-solid-svg-icons'

library.add(faFileUpload)

export default class UploadJobWidget extends Component {
  constructor (props) {
    super(props)

    this.JOB_UPLOAD_STARTED = 'A job upload to the printer has been started'
    this.JOB_UPLOAD_SUCCESS = 'A new job was successfully uploaded to the printer'
    this.JOB_UPLOAD_FAILED = 'There was a problem uploading the job to the printer'
  }

  handleFileChange = (event) => {
    const file = event.target.files[0]
    if (!file) {
      return
    }

    const fileName = file.name
    this.context.mutations.setUploadFilename(fileName)

    this.showUploadPercentage()
    this.submitFile(file)
  }

  handleUploadSuccess = () => {
    this.context.mutations.setUploadPercentage(-1)
    this.fileInput.value = ''
    this.context.mutations.logMessage(this.JOB_UPLOAD_SUCCESS)
  }

  showUploadPercentage = () => {
    this.context.mutations.setUploadPercentage(0)
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
      this.fileInput.value = ''
      this.context.mutations.logMessage(this.JOB_UPLOAD_FAILED)
    })
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Col sm={this.props.size}>
            <label className='file-select'>
              <div className='upload-button btn'>
                <p>{this.props.size !== '3' && <FontAwesomeIcon icon='file-upload' />} { this.props.title }</p>
              </div>
              <input
                className='input_file'
                onChange={(event) => { this.handleFileChange(event) }}
                ref={(ref) => { this.fileInput = ref }}
                type='file'
              />
            </label>
          </Col>
        )}
      </AppConsumer>
    )
  }
}
UploadJobWidget.contextType = AppContext
