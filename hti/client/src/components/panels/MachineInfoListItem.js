import React, { Component } from 'react'
import { ListGroupItem } from 'reactstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { AppConsumer } from '../../context/AppContext'
import PropTypes from 'prop-types'

export default class MachineInfoListItem extends Component {
  getDateString (dateString) {
    const regex = /(?<years>[0-9]{4})([/-])(?<months>[0-9]{2})[/-](?<days>[0-9]{2}).*(?<hours>[0-9]{2})([/:])(?<minutes>[0-9]{2})[/:](?<seconds>[0-9]{2})?/
    const regexMatch = regex.exec(dateString)
    if (regexMatch) {
      const years = regexMatch.groups.years || '0000'
      const months = regexMatch.groups.months || '00'
      const days = regexMatch.groups.days || '00'
      const hours = regexMatch.groups.hours || '00'
      const minutes = regexMatch.groups.minutes || '00'
      const seconds = regexMatch.groups.seconds || '00'
      return years + '/' + months + '/' + days + ' ' + hours + ':' + minutes + ':' + seconds
    } else {
      return dateString
    }
 }

  render () {
    const { hmi_version, firmware_version, date, machine_info_id, network_info } = this.props
    return (
      <div>
        <AppConsumer>

          {({ mutations }) => (
            <ListGroupItem
              data-cy='MachineInfoListItem'
              id={'list-group-item-success-custom'}
              style={{ height: '60px' }}>

              <FontAwesomeIcon
                className='download_icon'
                style={{ float: 'left' }}
                data-cy='info-button'
                onClick={() => mutations.showMachineInfo(machine_info_id)}
                icon='info-circle' />

              <span className='gcode_text'
                onClick={() => mutations.showMachineInfo(machine_info_id)}
                style={{ float: 'left' }}>
                &nbsp;HMI ver : {hmi_version} / FW ver : {firmware_version}
              </span>

              <span style={{ float: 'right' }}>
                {
                  (Number(network_info) > 0) &&
                    <FontAwesomeIcon
                      className='network_icon'
                      data-cy='network-button'
                      onClick={() => mutations.showNetworkInfo(machine_info_id)}
                      icon='network-wired' />
                }
                &nbsp;
                <span className='result_text' style={{ float: 'right' }}
                  onClick={() => mutations.showMachineInfo(machine_info_id)}>
                  { this.getDateString(date) }
                </span>
              </span>
            </ListGroupItem>
          )}
        </AppConsumer>
      </div>
    )
  }
}

MachineInfoListItem.propTypes = {
  network_info: PropTypes.string,
  machine_info_id: PropTypes.string,
  date: PropTypes.string,
  hmi_version: PropTypes.string,
  firmware_version: PropTypes.string
}
