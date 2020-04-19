import React, { Component } from 'react'
import { ListGroupItem } from 'reactstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { AppContext, AppConsumer } from '../../context/AppContext'
import PropTypes from 'prop-types'

export default class ReportListItem extends Component {
  render () {
    const { name, result, date, filename } = this.props
    return (
      <div>
        <AppConsumer>

          {({ mutations }) => (
            <ListGroupItem
              data-cy='list-item'
              id={result === 'finish' ? 'list-group-item-success-custom' : 'list-group-item-abort-custom'}>

              <FontAwesomeIcon
                className='download_icon'
                style={{ float: 'left' }}
                data-cy='info-button'
                icon='file-archive'
                onClick={() => mutations.downloadReportFile(filename)} />

              <span className='gcode_text' style={{ float: 'left' }}>
                &nbsp;{name}.gcode
              </span>

              <span className='download_icon'>
              &nbsp;
              </span>

              <span style={{ float: 'right' }}>
                <table>
                  <tbody>
                    <tr>
                      <td>
                        <span className='result_text' style={{ float: 'right' }}>
                          {result === 'finish' ? 'success' : 'aborted / error'}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td>
                        <span className='result_text' style={{ float: 'right' }}>
                          { date.substring(0, 4) }/{ date.substring(4, 6) }/{ date.substring(6, 8) }
                          &nbsp;{ date.substring(8, 10) }:{ date.substring(10, 12) }:{ date.substring(12, 14) }
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </span>
            </ListGroupItem>
          )}
        </AppConsumer>
      </div>
    )
  }
}

ReportListItem.contextType = AppContext // This part is important to access context values

ReportListItem.propTypes = {
  filename: PropTypes.string,
  date: PropTypes.string,
  name: PropTypes.string,
  result: PropTypes.string
}
