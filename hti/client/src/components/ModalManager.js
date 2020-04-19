import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../context/AppContext'

import PrePrintCheckModal from './modals/PrePrintCheckModal'
import AbortJobModal from './modals/AbortJobModal'
import StayHotModal from './modals/StayHotModal'
import DemoModeModal from './modals/DemoModeModal'
import OOFModal from './modals/OOFModal'
import ChangeFilamentModal from './modals/ChangeFilamentModal'
import MachineInfoModal from './modals/MachineInfoModal'
import NetworkInfoModal from './modals/NetworkInfoModal'
import ConfirmHomeModal from './modals/ConfirmHomeModal'
import OffSetModal from './modals/OffSetModal'
import UnlockDoorModal from './modals/UnlockDoorModal'
import ResumeJobModal from './modals/ResumeJobModal'
import CalibrateExtrusionRateModal from './modals/CalibrateExtrusionRateModal'
import SelectExtruderTypeModal from './modals/SelectExtruderTypeModal'
import { CommandsModal, EStopModal, GenericInfoModal, WrongFirmwareModal } from './modals/Modals'


export default class ModalManager extends Component {

  render () {
    const currentModal = this.context.store.currentModal
    const initialized = this.context.store.InitialDataLoaded && this.context.store.machineInfo

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div>
            { initialized && mutations.eStopTriggered() && <EStopModal /> }
            { initialized && !mutations.eStopTriggered() && (
              <div>
                { store.machineInfo.isRequiredFirmwareVersion === false && <WrongFirmwareModal /> }
                { currentModal === 'showPrePrintCheckModal' && <PrePrintCheckModal /> }
                { currentModal === 'showAbortModal' && <AbortJobModal /> }
                { currentModal === 'showStayHotModal' && <StayHotModal /> }
                { currentModal === 'showDemoModeModal' && <DemoModeModal /> }
                { currentModal === 'showOOFModal' && <OOFModal /> }
                { currentModal === 'showChangeFilamentModalT0' && <ChangeFilamentModal tool='t0' /> }
                { currentModal === 'showChangeFilamentModalT1' && <ChangeFilamentModal tool='t1' /> }
                { currentModal === 'showMachineInfoModal' && <MachineInfoModal /> }
                { currentModal === 'showNetworkInfoModal' && <NetworkInfoModal /> }
                { currentModal === 'showConfirmHomeModal' && <ConfirmHomeModal /> }
                { currentModal === 'showOffSetModal' && <OffSetModal disableOffsetInputs={false} /> }
                { currentModal === 'showUnlockDoorModal' && <UnlockDoorModal /> }
                { currentModal === 'showResumeModal' && <ResumeJobModal /> }
                { currentModal === 'showCalibrateExtrusionRateModalT0' && <CalibrateExtrusionRateModal tool='t0' /> }
                { currentModal === 'showCalibrateExtrusionRateModalT1' && <CalibrateExtrusionRateModal tool='t1' /> }
                { currentModal === 'showGenericInfoModal' && <GenericInfoModal /> }
                { currentModal === 'showMissingCommands' && <CommandsModal /> }
                { currentModal === 'showExtruderTypeModal' && store.machineInfo.extruderTypes[0].type !== null && store.machineInfo.extruderTypes[1].type !== null && <SelectExtruderTypeModal /> }
              </div>
            )}
          </div>
        )}
      </AppConsumer>
    )
  }
}

ModalManager.contextType = AppContext
