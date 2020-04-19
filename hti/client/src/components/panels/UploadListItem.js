import React, { Component } from 'react'
import { ListGroupItem, Col, Row, Progress } from 'reactstrap'
import { AppContext } from '../../context/AppContext'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faInfoCircle, faTrashAlt, faPlay, faCogs, faBars, faNetworkWired, faArrowCircleUp, faSpinner } from '@fortawesome/free-solid-svg-icons'

library.add(faInfoCircle, faTrashAlt, faPlay, faCogs, faBars, faNetworkWired, faArrowCircleUp, faSpinner)

export default class UploadListItem extends Component {
  render () {
    const isUploading = (this.context.store.uploadPercentage > -1 && this.context.store.uploadPercentage <= 100)
    const uploadFilename = this.context.store.uploadFilename
    const uploadPercentage = this.context.store.uploadPercentage

    return (
      <div>
      {
        isUploading &&
        <ListGroupItem
          data-cy='ListItem'
          className={'upload-job-item'}>
          <Row>
            <Col>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ margin: '0', display: 'flex' }}>
                  <FontAwesomeIcon icon='arrow-circle-up' />
                  <span style={{ width: '800px' }}>
                    <span className='file_list_text'>{uploadFilename} ({uploadPercentage}%)</span>
                  </span>
                </h2>
              </div>
            </Col>
          </Row>
          <Row>
            <Col>
              <Progress value={uploadPercentage} color='#dd5d37' height='4px' />
            </Col>
          </Row>
        </ListGroupItem>
      }
      </div>
    )
  }
}
UploadListItem.contextType = AppContext
