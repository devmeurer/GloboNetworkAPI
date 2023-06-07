# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.api_vrf.exceptions import VrfAssociatedToVlanEquipment
from networkapi.api_vrf.exceptions import VrfAssociatedToVirtualInterface
from networkapi.api_vrf.exceptions import VrfError
from networkapi.api_vrf.exceptions import VrfNotFoundError
from networkapi.api_vrf.exceptions import VrfRelatedToEnvironment
from networkapi.filter.models import FilterNotFoundError
from networkapi.models.BaseModel import BaseModel


class Vrf(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    vrf = models.TextField(
        max_length=45,
        db_column='vrf'
    )
    internal_name = models.TextField(
        max_length=45,
        db_column='internal_name'
    )

    log = logging.getLogger('Vrf')

    @classmethod
    def get_by_pk(cls, id_vrf):
        """Get Vrf by id.

        @return: Vrf.

        @raise VrfNotFoundError: Vrf is not registered.
        @raise VrfError: Failed to search for the Vrf.
        @raise OperationalError: Lock wait timeout exceed
        """
        try:
            return Vrf.objects.filter(id=id_vrf).uniqueResult()
        except ObjectDoesNotExist as e:
            raise VrfNotFoundError(
                'Vrf id = %s does not exist.' % id_vrf)
        except OperationalError as e:
            cls.log.error('Lock wait timeout exceeded.')
            raise OperationalError(
                'Lock wait timeout exceeded; try restarting transaction')
        except Exception as e:
            cls.log.error('Failure to search the Vrf. Error: {}'.format(e))
            raise VrfError('Failure to search the Vrf. Error: {}'.format(e))

    def create(self, authenticated_user):
        """Include new Vrf.

        @return: Id new Vrf

        @raise FilterNotFoundError: Dont' exist filter for pk searched
        """

        try:
            return self.save()

        except FilterNotFoundError as e:
            raise e
        except Exception:
            self.log.error('Fail on inserting Vrf.')

    @classmethod
    def update(cls, authenticated_user, pk, **kwargs):
        """Change some Vrf.

        @return: Nothing

        @raise VrfNotFoundError: It doesn't exist Vrf for searched pk.

        @raise CannotDissociateFilterError: Filter in use, can't be dissociated.
        """
        vrf = Vrf().get_by_pk(pk)

        try:
            try:
                Vrf.objects.get(id=pk)
            except Vrf.DoesNotExist:
                pass

            vrf.__dict__.update(kwargs)
            vrf.save(authenticated_user)

        except Exception as e:
            cls.log.error('Fail to change Vrf. Error: {}'.format(e))

    @classmethod
    def remove(cls, pk):
        """Remove vrf.

        @return: Nothing

        @raise VrfNotFoundError: It doesn' exist Vrf to searched id

        @raise VrfRelatedToEnvironment: At least one Environment is using this Vrf

        @raise VrfAssociatedToVlanEquipment: At least one Vlan and Equipment are
                                             associated together to this Vrf

        """

        vrf = Vrf().get_by_pk(pk)

        entry_env = vrf.ambiente_set.all()

        if len(entry_env) > 0:
            cls.log.error('Fail to remove Vrf.')
            raise VrfRelatedToEnvironment(
                'Vrf with pk = %s is being used at some environment.' %
                pk)

        entry_vlan_eqpt = VrfVlanEquipment.objects.filter(vrf=pk)

        if len(entry_vlan_eqpt) > 0:
            cls.log.error('Fail to remove Vrf.')
            raise VrfAssociatedToVlanEquipment(
                'Vrf with pk = %s is associated to some Vlan and Equipment.' %
                pk)

        # Remove assoc between Vrf and Equipment
        VrfEquipment.objects.filter(vrf=pk).delete()

        # Remove Vrf
        vrf.delete()

    class Meta (BaseModel.Meta):
        managed = True
        db_table = 'vrf'


class VrfVlanEquipment(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    vrf = models.ForeignKey(
        Vrf,
        db_column='id_vrf',
        null=False,
        on_delete=models.DO_NOTHING
    )
    vlan = models.ForeignKey(
        'vlan.Vlan',
        db_column='id_vlan',
        null=False,
        on_delete=models.DO_NOTHING
    )
    equipment = models.ForeignKey(
        'equipamento.Equipamento',
        db_column='id_equipment',
        null=False,
        on_delete=models.DO_NOTHING
    )

    log = logging.getLogger('VrfVlanEquipment')

    class Meta (BaseModel.Meta):
        db_table = 'vrf_vlan_eqpt'
        managed = True
        unique_together = ('vlan', 'equipment')


class VrfEquipment(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    vrf = models.ForeignKey(
        'api_vrf.Vrf',
        db_column='id_vrf',
        null=False,
        on_delete=models.DO_NOTHING
    )
    equipment = models.ForeignKey(
        'equipamento.Equipamento',
        db_column='id_equipment',
        null=False,
        on_delete=models.DO_NOTHING
    )
    internal_name = models.TextField(
        max_length=45,
        db_column='internal_name'
    )

    log = logging.getLogger('VrfVlanEquipment')

    class Meta (BaseModel.Meta):
        db_table = 'vrf_eqpt'
        managed = True
        unique_together = ('vrf', 'equipment')
