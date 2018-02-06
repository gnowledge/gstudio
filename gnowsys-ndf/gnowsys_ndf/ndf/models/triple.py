from base_imports import *
from node import *
from db_utils import get_model_name

#  TRIPLE CLASS DEFINITIONS
@connection.register
class Triple(DjangoDocument):

  objects = models.Manager()

  collection_name = 'Triples'
  structure = {
    '_type': unicode,
    'name': unicode,
    'subject_scope': basestring,
    'object_scope': basestring,
    'subject': ObjectId,  # ObjectId's of GSystem Class
    'language': (basestring, basestring),  # e.g: ('en', 'English') or ['en', 'English']
    'status': STATUS_CHOICES_TU
  }

  required_fields = ['name', 'subject']
  use_dot_notation = True
  use_autorefs = True
  default_values = {
                      'subject_scope': None,
                      'object_scope': None
                  }

  @classmethod
  def get_triples_from_sub_type(cls, subject_id, gt_or_rt_name_or_id, status=None):
        '''
        getting triples from SUBject and TYPE (attribute_type or relation_type)
        '''
        triple_node_mapping_dict = {
            'GAttribute': 'AttributeType',
            'GRelation': 'RelationType'
        }
        triple_class_field_mapping_dict = {
            'GAttribute': 'attribute_type',
            'GRelation': 'relation_type'
        }
        gr_or_rt_name, gr_or_rt_id = Node.get_name_id_from_type(gt_or_rt_name_or_id,
            triple_node_mapping_dict[get_model_name(cls) ])
        status = [status] if status else ['PUBLISHED', 'DELETED']
        return triple_collection.find({
                                    '_type': get_model_name(cls),
                                    'subject': ObjectId(subject_id),
                                    triple_class_field_mapping_dict[get_model_name(cls)]: gr_or_rt_id,
                                    'status': {'$in': status}
                                })


  @classmethod
  def get_triples_from_sub_type_list(cls, subject_id, gt_or_rt_name_or_id_list, status=None, get_obj=True):
        '''
        getting triples from SUBject and TYPE (attribute_type or relation_type)
        '''
        triple_node_mapping_dict = {
            'GAttribute': 'AttributeType',
            'GRelation': 'RelationType'
        }
        triple_class_field_mapping_dict = {
            'GAttribute': 'attribute_type',
            'GRelation': 'relation_type'
        }
        triple_class_field_mapping_key_dict = {
            'GAttribute': 'object_value',
            'GRelation': 'right_subject'
        }

        if not isinstance(gt_or_rt_name_or_id_list, list):
            gt_or_rt_name_or_id_list = [gt_or_rt_name_or_id_list]

        gt_or_rt_id_name_dict = {}
        for each_gr_or_rt in gt_or_rt_name_or_id_list:
            gr_or_rt_name, gr_or_rt_id = Node.get_name_id_from_type(each_gr_or_rt,
                triple_node_mapping_dict[get_model_name(cls)])
            gt_or_rt_id_name_dict.update({gr_or_rt_id: gr_or_rt_name})

        status = [status] if status else ['PUBLISHED', 'DELETED']

        tr_cur = triple_collection.find({
                                    '_type': get_model_name(cls),
                                    'subject': ObjectId(subject_id),
                                    triple_class_field_mapping_dict[get_model_name(cls)]: {'$in': gt_or_rt_id_name_dict.keys()},
                                    'status': {'$in': status}
                                })

        gt_or_rt_name_value_or_obj_dict = {gt_or_rt: '' for gt_or_rt in gt_or_rt_name_or_id_list}
        for each_tr in tr_cur:
            gt_or_rt_name_value_or_obj_dict[gt_or_rt_id_name_dict[each_tr[triple_class_field_mapping_dict[get_model_name(cls)]]]] = each_tr if get_obj else each_tr[triple_class_field_mapping_key_dict[get_model_name(cls)]]
        return gt_or_rt_name_value_or_obj_dict


  ########## Built-in Functions (Overridden) ##########
  def __unicode__(self):
    return self._id

  def identity(self):
    return self.__unicode__()

  def save(self, *args, **kwargs):
    is_new = False
    if "_id" not in self:
      is_new = True  # It's a new document, hence yet no ID!"

    """
    Check for correct GSystemType match in AttributeType and GAttribute, similarly for RelationType and GRelation
    """
    subject_system_flag = False

    subject_id = self.subject
    subject_document = node_collection.one({"_id": self.subject})
    if not subject_document:
        return
    subject_name = subject_document.name
    right_subject_member_of_list = []

    subject_type_list = []
    subject_member_of_list = []
    name_value = u""
    # if (self._type == "GAttribute") and ('triple_node' in kwargs):
    if (self._type == "GAttribute"):
      # self.attribute_type = kwargs['triple_node']
      at_node = node_collection.one({'_id': ObjectId(self.attribute_type)})
      attribute_type_name = at_node.name
      attribute_object_value = unicode(self.object_value)
      attribute_object_value_for_name = attribute_object_value[:20]
      self.name = "%(subject_name)s -- %(attribute_type_name)s -- %(attribute_object_value_for_name)s" % locals()
      name_value = self.name

      subject_type_list = at_node.subject_type
      subject_member_of_list = subject_document.member_of

      intersection = set(subject_member_of_list) & set(subject_type_list)
      if intersection:
        subject_system_flag = True

      else:
        # If instersection is not found with member_of fields' ObjectIds,
        # then check for type_of field of each one of the member_of node
        for gst_id in subject_member_of_list:
          gst_node = node_collection.one({'_id': gst_id}, {'type_of': 1})
          if set(gst_node.type_of) & set(subject_type_list):
            subject_system_flag = True
            break
      # self.attribute_type = kwargs['triple_id']

    elif self._type == "GRelation":
      rt_node = node_collection.one({'_id': ObjectId(self.relation_type)})
      # self.relation_type = kwargs['triple_node']
      subject_type_list = rt_node.subject_type
      object_type_list = rt_node.object_type

      left_subject_member_of_list = subject_document.member_of
      relation_type_name = rt_node.name
      if META_TYPE[4] in rt_node.member_of_names_list:
        #  print META_TYPE[3], self.relation_type.member_of_names_list,"!!!!!!!!!!!!!!!!!!!!!"
        # Relationship Other than Binary one found; e.g, Triadic
        # Single relation: [ObjectId(), ObjectId(), ...]
        # Multi relation: [[ObjectId(), ObjectId(), ...], [ObjectId(), ObjectId(), ...], ...]
        right_subject_member_of_list = []
        right_subject_member_of_list_append = right_subject_member_of_list.append

        right_subject_name_list = []
        right_subject_name_list_append = right_subject_name_list.append
        print self.right_subject,"%%%%%%%%%%%%%",type(self.right_subject)
        for each in self.right_subject:
          # Here each is an ObjectId
          right_subject_document = node_collection.one({
            "_id": each
          }, {
            "name": 1, "member_of": 1
          })

          right_subject_member_of_list_append(right_subject_document.member_of)
          right_subject_name_list_append(right_subject_document.name)

        right_subject_name_list_str = " >> ".join(right_subject_name_list)

        self.name = "%(subject_name)s -- %(relation_type_name)s -- %(right_subject_name_list_str)s" % locals()

        # Very much required as list comparison using set doesn't work
        # with list as it's sub-elements
        # Hence, converting list into comma separated values by extending
        # with other comma-separated values from another list(s)
        object_type_list = list(chain.from_iterable(object_type_list))
        right_subject_member_of_list = list(chain.from_iterable(right_subject_member_of_list))
      else:
          #META_TYPE[3] in self.relation_type.member_of_names_list:
          # If Binary relationship found
          # Single relation: ObjectId()
          # Multi relation: [ObjectId(), ObjectId(), ...]

          right_subject_list = self.right_subject if isinstance(self.right_subject, list) else [self.right_subject]
          right_subject_document = node_collection.find_one({'_id': {'$in': right_subject_list} })
          if right_subject_document:
              right_subject_member_of_list = right_subject_document.member_of
              right_subject_name = right_subject_document.name

              self.name = "%(subject_name)s -- %(relation_type_name)s -- %(right_subject_name)s" % locals()

      name_value = self.name

      left_intersection = set(subject_type_list) & set(left_subject_member_of_list)
      right_intersection = set(object_type_list) & set(right_subject_member_of_list)
      if left_intersection and right_intersection:
        subject_system_flag = True
      else:
        left_subject_system_flag = False
        if left_intersection:
          left_subject_system_flag = True
        else:
          for gst_id in left_subject_member_of_list:
            gst_node = node_collection.one({'_id': gst_id}, {'type_of': 1})
            if set(gst_node.type_of) & set(subject_type_list):
              left_subject_system_flag = True
              break


        right_subject_system_flag = False
        if right_intersection:
          right_subject_system_flag = True

        else:
          for gst_id in right_subject_member_of_list:
            gst_node = node_collection.one({'_id': gst_id}, {'type_of': 1})
            if set(gst_node.type_of) & set(object_type_list):
              right_subject_system_flag = True
              break

        if left_subject_system_flag and right_subject_system_flag:
          subject_system_flag = True

      # self.relation_type = kwargs['triple_id']

    if self._type =="GRelation" and subject_system_flag == False:
      # print "The 2 lists do not have any common element"
      raise Exception("\n Cannot create the GRelation ("+name_value+") as the subject/object that you have mentioned is not a member of a GSytemType for which this RelationType is defined!!!\n")

    if self._type =="GAttribute" and subject_system_flag == False:
      # print "\n The 2 lists do not have any common element\n"
      error_message = "\n "+name_value+ " -- subject_type_list ("+str(subject_type_list)+") -- subject_member_of_list ("+str(subject_member_of_list)+") \n"
      raise Exception(error_message + "Cannot create the GAttribute ("+name_value+") as the subject that you have mentioned is not a member of a GSystemType which this AttributeType is defined")

    #it's me
    #check for data_type in GAttribute case. Object value of the GAttribute must have the same type as that of the type specified in AttributeType
    """if self._type == "GAttribute": data_type_in_attribute_type =
    self.attribute_type['data_type'] data_type_of_object_value =
    type(self.object_value) print "Attribute:: " +
    str(data_type_in_attribute_type) print "Value:: " +
    str(data_type_of_object_value) if data_type_in_attribute_type !=
    data_type_of_object_value: raise Exception("The DataType of the
    value you have entered for this attribute is not correct. Pls ener
    a value with type ---> " + str(data_type_in_attribute_type))

    """
    #end of data_type_check

    super(Triple, self).save(*args, **kwargs)

    history_manager = HistoryManager()
    rcs_obj = RCS()
    if is_new:
      # Create history-version-file
      if history_manager.create_or_replace_json_file(self):
        fp = history_manager.get_file_path(self)
        message = "This document (" + self.name + ") is created on " + datetime.datetime.now().strftime("%d %B %Y")
        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

    else:
      # Update history-version-file
      fp = history_manager.get_file_path(self)

      try:
          rcs_obj.checkout(fp, otherflags="-f")
      except Exception as err:
          try:
              if history_manager.create_or_replace_json_file(self):
                  fp = history_manager.get_file_path(self)
                  message = "This document (" + self.name + ") is re-created on " + datetime.datetime.now().strftime("%d %B %Y")
                  rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

          except Exception as err:
              print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be re-created!!!\n"
              node_collection.collection.remove({'_id': self._id})
              raise RuntimeError(err)

      try:
          if history_manager.create_or_replace_json_file(self):
              message = "This document (" + self.name + ") is lastly updated on " + datetime.datetime.now().strftime("%d %B %Y")
              rcs_obj.checkin(fp, 1, message.encode('utf-8'))

      except Exception as err:
          print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be updated!!!\n"
          raise RuntimeError(err)


triple_collection   = db["Triples"].Triple