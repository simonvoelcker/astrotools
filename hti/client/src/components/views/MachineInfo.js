import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { Row, Col } from 'reactstrap'
import Logo from '../../assets/img/BigRep.svg'
import MachineInfoListItem from '../../components/panels/MachineInfoListItem'
import VersionInfo from '../../components/panels/VersionInfo'
import ModalManager from '../../components/ModalManager'

import { library } from '@fortawesome/fontawesome-svg-core'
import { faFileArchive } from '@fortawesome/free-solid-svg-icons'

library.add(faFileArchive)

export default class MachineInfo extends Component {
  componentWillMount () {
    this.context.mutations.updateMachineInfoList()
  }

  hasNetworkInfo = (network_info) => {
    return network_info !== undefined ? network_info.length+'' : ''
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
                  <h4>Machine Infos</h4>
                </Col>
                <Col sm={4} align={'right'} />
              </Row>

              {/* Contents Area */}
              <Row>
                <Col sm={1} />
                <Col sm={10}>
                  {
                    store.machineInfoList && store.machineInfoList[0] ? (
                      <div className='scrollable' style={{ marginTop: '2rem' }}>
                        {store.machineInfoList.map((value, index) => (
                          <MachineInfoListItem
                            key={value._id}
                            hmi_version={value.machine_meta_info.version}
                            firmware_version={value.machine_meta_info.firmwareVersion}
                            date={value.created_at}
                            machine_info_id={value._id}
                            network_info={this.hasNetworkInfo(value.network_info)} />
                        ))}
                      </div>
                    ) : (<h1 style={{ textAlign: 'center' }}>NO MACHINE INFO</h1>)
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
MachineInfo.contextType = AppContext // This part is important to access context values
