import React, { Component } from 'react'
import { Row, Col, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { ButtonDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export default class SelectExtruderTypeModal extends Component {
   constructor (props) {
    super(props)
    this.state = {
      t0DropdownOpen: false,
      t1DropdownOpen: false,
      t0Selected: {type: 1, name: 'MXT'},
      t1Selected: {type: 2, name: 'ACE'}
    }
  }

  componentDidMount () {
    const extruderTypes = this.context.store.machineInfo.extruderTypes
    const t0 = extruderTypes[0]
    const t1 = extruderTypes[1]
    if (t0.type !== null && t0.desc !== null) {
      this.setState({ t0Selected: {type: t0.type, name: t0.desc} })
    }
    if (t1.type !== null && t1.desc !== null) {
      this.setState({ t1Selected: {type: t1.type, name: t1.desc} })
    }
  }

  t0Toggle = () => {
    this.setState({t0DropdownOpen: !this.state.t0DropdownOpen})
  }

  t1Toggle = () => {
    this.setState({t1DropdownOpen: !this.state.t1DropdownOpen})
  }

  t0HandleChange = (extruder_type) => {
    this.setState({ t0Selected: extruder_type })
  }

  t1HandleChange = (extruder_type) => {
    this.setState({ t1Selected: extruder_type })
  }

  saveExtruderInfo = (t0, t1) => {
    let extruders = []

    if (t0.type === null || this.context.store.showExtruderTypeModal) {
      extruders.push({
        name: t0.name, serialNumber: t0.serialNumber, old_type:t0.type,
        type: this.state.t0Selected.type, desc: this.state.t0Selected.name
      })
    } else {
      extruders.push(t0)
    }

    if (t1.type === null || this.context.store.showExtruderTypeModal) {
      extruders.push({
        name: t1.name, serialNumber: t1.serialNumber, old_type:t1.type,
        type: this.state.t1Selected.type, desc: this.state.t1Selected.name
      })
    } else {
      extruders.push(t1)
    }

    this.context.mutations.setExtruders(extruders)
    if (this.context.store.showExtruderTypeModal) {
      this.context.mutations.toggleModal('showExtruderTypeModal')
    }
  }

  render () {
    const extruderTypes = this.context.store.machineInfo.extruderTypes
    const t0 = extruderTypes[0]
    const t1 = extruderTypes[1]
    const extruder_types = [
      {type:1, name:'MXT'},
      {type:2, name:'ACE'}
    ]

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} data-cy='SelectExtruderTypeModal'>
            <ModalHeader>Set Extruder Types</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>Select correct type for Extruder.</p>
              <div>
                {(t0.type === null || store.showExtruderTypeModal) &&
                  <Row style={{ padding: '0.5rem' }}>
                    <Col sm={5} style={{display:'flex', alignItems: 'center'}}><h4>T0: {extruderTypes[0].serialNumber}</h4></Col>
                    <Col sm={5}>
                      <ButtonDropdown isOpen={this.state.t0DropdownOpen} toggle={this.t0Toggle}>
                        <DropdownToggle caret color="primary">
                          <font style={{color:'white'}}>{ this.state.t0Selected.name }</font>
                        </DropdownToggle>
                        <DropdownMenu>
                          {extruder_types.map((value, index) => (
                            <DropdownItem key={value.type} onClick={() => this.t0HandleChange(value)}>
                            <font style={{color:'white'}}>{ value.name }</font>
                            </DropdownItem>
                          ))}
                        </DropdownMenu>
                      </ButtonDropdown>
                    </Col>
                  </Row>
                }
                {(t1.type === null || store.showExtruderTypeModal) &&
                  <Row style={{ padding: '0.5rem' }}>
                    <Col sm={5} style={{display:'flex', alignItems: 'center'}}><h4>T1: {extruderTypes[1].serialNumber}</h4></Col>
                    <Col sm={5}>
                      <ButtonDropdown isOpen={this.state.t1DropdownOpen} toggle={this.t1Toggle}>
                        <DropdownToggle caret color="primary">
                          <font style={{color:'white'}}>{ this.state.t1Selected.name }</font>
                        </DropdownToggle>
                        <DropdownMenu>
                          {extruder_types.map((value, index) => (
                            <DropdownItem key={value.type} onClick={() => this.t1HandleChange(value)}>
                            <font style={{color:'white'}}>{ value.name }</font>
                            </DropdownItem>
                          ))}
                        </DropdownMenu>
                      </ButtonDropdown>
                    </Col>
                  </Row>
                }
              </div>
            </ModalBody>
            <ModalFooter>
              <StandardButton
                datacy={'ExtruderSaveButton'}
                color='secondary'
                onClick={() => this.saveExtruderInfo(t0, t1) }
              >Save</StandardButton>
              { store.showExtruderTypeModal &&
                <StandardButton
                  datacy={'ExtruderCloseButton'}
                  color='secondary'
                  onClick={() => mutations.toggleModal('showExtruderTypeModal') }
                >Close</StandardButton>
              }
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

SelectExtruderTypeModal.contextType = AppContext
