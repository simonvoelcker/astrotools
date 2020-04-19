import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { Row, Col } from 'reactstrap'
import { formatMemory } from '../../Utils.js'
import Logo from '../../assets/img/BigRep.svg'
import VersionInfo from '../../components/panels/VersionInfo'
import UploadJobWidget from '../../components/panels/UploadJobWidget'
import JobList from '../panels/JobList'
import ModalManager from '../../components/ModalManager'

export default class Manage extends Component {
  formatFreeDiskSpace = (info) => {
    if (info == null) {
      return 'unknown'
    }
    return formatMemory(info.bytes_free) + ' free'
  }

  componentWillMount () {
    this.context.mutations.updateDiskInfo()
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='view-manage'>
            <VersionInfo />
            <div className='container'>
              <Row>
                <Col sm={4}>
                  <img src={Logo} alt='logo' width='80%' />
                  <h4>Job Management</h4>
                </Col>
                <Col sm={4} align={'middle'}>
                  <p className='spitzmarke' data-cy='DiskSpace'>Disk: {this.formatFreeDiskSpace(store.diskInfo)}</p>
                </Col>
                <UploadJobWidget title="UPLOAD JOB" size="4"/>
              </Row>
              {store.InitialDataLoaded ? <JobList scene='Manage' /> : ''}
            </div >
            <ModalManager />
          </div >
        )}
      </AppConsumer>
    )
  }
}
Manage.contextType = AppContext
