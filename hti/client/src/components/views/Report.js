import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { Row, Col } from 'reactstrap'
import Logo from '../../assets/img/BigRep.svg'
import ReportListItem from '../../components/panels/ReportListItem'
import VersionInfo from '../../components/panels/VersionInfo'
import ModalManager from '../../components/ModalManager'

import { library } from '@fortawesome/fontawesome-svg-core'
import { faFileArchive } from '@fortawesome/free-solid-svg-icons'

library.add(faFileArchive)

export default class Report extends Component {
  componentWillMount () {
    this.context.mutations.updateReportList()
  }
  render () {
    return (
      <AppConsumer>

        {({ store, mutations }) => (
          <div className='view-report'>
            <VersionInfo />

            <div className='container'>

              {/* Top Area */}
              <Row>
                <Col sm={4}>
                  <img src={Logo} alt='logo' width='80%' />
                  <h4>Job Reports</h4>
                </Col>
                <Col sm={4} align={'right'} />
              </Row>

              {/* Contents Area */}
              <Row>
                <Col sm={1} />
                <Col sm={10}>
                  {
                    store.jobReports.files && store.jobReports.files[0] ? (
                      <div className='scrollable' style={{ marginTop: '2rem' }}>
                        {store.jobReports.files.map((value, index) => (
                          <ReportListItem
                            key={value.filename}
                            name={value.archiveJobName}
                            result={value.archiveResult}
                            date={value.archiveDate}
                            filename={value.filename} />
                        ))}
                      </div>
                    ) : (<h1 style={{ textAlign: 'center' }}>NO REPORT FILE</h1>)
                  }
                </Col>
                <Col sm={1} />
              </Row>
            </div >
            <ModalManager />
          </div >
        )}
      </AppConsumer>
    )
  }
}
Report.contextType = AppContext // This part is important to access context values
