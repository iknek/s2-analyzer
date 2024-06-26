import ActuatorDescription from "../../dataStructures/frbc/actuatorDescription";
import StorageDescription from "../../dataStructures/frbc/storageDescription";
import MessageHeader from "../messageHeader";

export default interface SystemDescription extends MessageHeader {
  valid_from: Date;
  actuators: ActuatorDescription[];
  storage: StorageDescription[];
}
