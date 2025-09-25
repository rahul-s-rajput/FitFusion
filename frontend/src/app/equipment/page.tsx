'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  Plus, 
  Search, 
  Filter, 
  Dumbbell, 
  Settings, 
  Trash2, 
  Edit, 
  CheckCircle, 
  XCircle,
  Package,
  Lightbulb,
  Star,
  AlertTriangle,
  Sparkles
} from 'lucide-react';

import { useEquipment, useEquipmentActions, useUIActions } from '../../store';
import { apiClient } from '../../lib/api-client';
import { Equipment } from '../../lib/db';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { PageHero, type HeroStat } from '../../components/workouts/page-hero';
import { SectionHeader } from '../../components/workouts/section-header';
import { QuickStatCard } from '../../components/workouts/quick-stat-card';
import { MobileBottomNav } from '../../components/workouts/mobile-bottom-nav';

export default function EquipmentPage() {
  const router = useRouter();
  const equipment = useEquipment();
  const { setEquipmentInventory, setEquipmentSuggestions, setEquipmentLoading } = useEquipmentActions();
  const { setCurrentPage, addNotification, setModalOpen } = useUIActions();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showAvailableOnly, setShowAvailableOnly] = useState(false);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);

  const categories = [
    { value: 'all', label: 'All Equipment' },
    { value: 'weights', label: 'Weights' },
    { value: 'cardio', label: 'Cardio' },
    { value: 'resistance', label: 'Resistance' },
    { value: 'flexibility', label: 'Flexibility' },
    { value: 'bodyweight', label: 'Bodyweight' }
  ];

  useEffect(() => {
    setCurrentPage('equipment');
    loadEquipmentData();
  }, []);

  const loadEquipmentData = async () => {
    try {
      setEquipmentLoading(true);

      // Load user's equipment inventory
      const inventoryResponse = await apiClient.getEquipment();
      if (inventoryResponse.data) {
        setEquipmentInventory(inventoryResponse.data);
      }

      // Load equipment suggestions
      const suggestionsResponse = await apiClient.getEquipmentSuggestions({
        budget: 'moderate',
        space: 'medium',
        goals: 'general_fitness'
      });
      if (suggestionsResponse.data) {
        setEquipmentSuggestions(suggestionsResponse.data);
      }

    } catch (error) {
      console.error('Failed to load equipment data:', error);
      addNotification({
        type: 'error',
        title: 'Loading Error',
        message: 'Failed to load equipment data. Please try again.',
      });
    } finally {
      setEquipmentLoading(false);
    }
  };

  const filteredEquipment = equipment.inventory.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    const matchesAvailability = !showAvailableOnly || item.is_available;
    
    return matchesSearch && matchesCategory && matchesAvailability;
  });

  const handleAddEquipment = () => {
    setModalOpen('equipmentAdd', true);
  };

  const handleEditEquipment = (item: Equipment) => {
    setSelectedEquipment(item);
    setModalOpen('equipmentAdd', true);
  };

  const handleDeleteEquipment = async (item: Equipment) => {
    if (!item.id) return;

    try {
      await apiClient.deleteEquipment(item.id.toString());
      addNotification({
        type: 'success',
        title: 'Equipment Deleted',
        message: `${item.name} has been removed from your inventory.`,
      });
      loadEquipmentData(); // Refresh the list
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: 'Failed to delete equipment. Please try again.',
      });
    }
  };

  const handleToggleAvailability = async (item: Equipment) => {
    if (!item.id) return;

    try {
      await apiClient.updateEquipment(item.id.toString(), {
        is_available: !item.is_available
      });
      addNotification({
        type: 'success',
        title: 'Equipment Updated',
        message: `${item.name} is now ${!item.is_available ? 'available' : 'unavailable'}.`,
      });
      loadEquipmentData(); // Refresh the list
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: 'Failed to update equipment availability.',
      });
    }
  };

  if (equipment.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="text-muted-foreground">Loading your equipment...</p>
        </div>
      </div>
    );
  }



  const totalInventory = equipment.inventory.length;

  const availableCount = equipment.availableEquipment.length;

  const categoryCount = new Set(equipment.inventory.map((item) => item.category)).size;

  const suggestionsCount = equipment.suggestions.length;



  const heroStats: HeroStat[] = [

    {

      label: 'Total items',

      value: String(totalInventory),

      helper: 'In your home gym',

      icon: Dumbbell,

    },

    {

      label: 'Ready to use',

      value: String(availableCount),

      helper: 'Equipment available now',

      icon: CheckCircle,

    },

    {

      label: 'Categories',

      value: String(categoryCount),

      helper: 'Different training styles',

      icon: Filter,

    },

    {

      label: 'AI suggestions',

      value: String(suggestionsCount),

      helper: 'Personalised ideas',

      icon: Sparkles,

    },

  ];



  const quickStatsCards = [

    {

      title: 'Maintenance due',

      value: `${equipment.inventory.filter((item) => item.condition === 'needs_repair').length}`,

      helper: 'Items needing attention',

      icon: AlertTriangle,

    },

    {

      title: 'Excellent condition',

      value: `${equipment.inventory.filter((item) => item.condition === 'excellent').length}`,

      helper: 'Ready for high intensity',

      icon: Star,

    },

    {

      title: 'Quiet friendly',

      value: `${equipment.inventory.filter((item) => item.category === 'bodyweight').length}`,

      helper: 'No noise options',

      icon: Activity,

    },

    {

      title: 'Space saved',

      value: equipment.inventory.length > 0 ? `${Math.max(1, Math.round(equipment.inventory.length * 1.5))} sq ft` : 'N/A',

      helper: 'Estimated footprint',

      icon: Package,

    },

  ];



  const heroActions = (

    <>

      <Button size="lg" onClick={handleAddEquipment}>

        <Plus className="mr-2 h-4 w-4" />

        Add Equipment

      </Button>

      <Button size="lg" variant="secondary" onClick={() => router.push('/equipment/suggestions')}>

        <Sparkles className="mr-2 h-4 w-4" />

        View Suggestions

      </Button>

    </>

  );



  return (

    <div className="relative min-h-screen bg-gradient-to-b from-background via-background/95 to-background">

      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 pb-24 pt-6 sm:px-6 lg:pt-10">

        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>

          <PageHero

            eyebrow="Equipment"

            title="Optimise your training space"

            description="Manage inventory, track availability, and let the AI suggest smart additions for your setup."

            actions={heroActions}

            stats={heroStats}

          />

        </motion.div>



        <motion.div

          initial={{ opacity: 0, y: 20 }}

          animate={{ opacity: 1, y: 0 }}

          transition={{ duration: 0.4, delay: 0.1 }}

        >

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

            {quickStatsCards.map((stat, index) => (

              <motion.div

                key={stat.title}

                initial={{ opacity: 0, y: 12 }}

                animate={{ opacity: 1, y: 0 }}

                transition={{ duration: 0.3, delay: 0.05 * index }}

              >

                <QuickStatCard

                  title={stat.title}

                  value={stat.value}

                  helper={stat.helper}

                  icon={stat.icon}

                />

              </motion.div>

            ))}

          </div>

        </motion.div>



        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">

          <div className="space-y-6">

            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.15 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <SectionHeader

                    title="Inventory overview"

                    description="All equipment currently tracked in FitFusion."

                    action={

                      <Button size="sm" variant="outline" onClick={handleAddEquipment}>

                        <Plus className="mr-2 h-4 w-4" />

                        Add item

                      </Button>

                    }

                  />

                </CardHeader>

                <CardContent className="space-y-4">

                  {filteredEquipment.length > 0 ? (

                    filteredEquipment.map((item) => (

                      <motion.div

                        key={item.id ?? item.name}

                        className="rounded-2xl border border-border/60 bg-card/80 p-4 shadow-sm"

                        initial={{ opacity: 0, y: 12 }}

                        animate={{ opacity: 1, y: 0 }}

                      >

                        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">

                          <div className="space-y-1">

                            <div className="flex items-center gap-2">

                              <h3 className="text-base font-semibold">{item.name}</h3>

                              <Badge className="capitalize" variant="outline">{item.category}</Badge>

                            </div>

                            <p className="text-xs text-muted-foreground">Condition: {item.condition.replace('_', ' ')}</p>

                            {item.is_available ? (

                              <p className="text-xs text-emerald-600">Available for sessions</p>

                            ) : (

                              <p className="text-xs text-muted-foreground">Currently unavailable</p>

                            )}

                          </div>

                          <div className="flex gap-2">

                            <Button variant="outline" size="sm" onClick={() => handleEditEquipment(item)}>

                              <Edit className="mr-2 h-4 w-4" />

                              Edit

                            </Button>

                            <Button variant="outline" size="sm" onClick={() => handleToggleAvailability(item)}>

                              <CheckCircle className="mr-2 h-4 w-4" />

                              {item.is_available ? 'Mark unavailable' : 'Mark available'}

                            </Button>

                            <Button variant="outline" size="sm" onClick={() => handleDeleteEquipment(item)}>

                              <Trash2 className="mr-2 h-4 w-4" />

                              Remove

                            </Button>

                          </div>

                        </div>

                      </motion.div>

                    ))

                  ) : (

                    <div className="rounded-2xl border border-dashed border-border/60 bg-muted/20 p-8 text-center text-sm text-muted-foreground">

                      {equipment.inventory.length === 0 ? 'Start building your home gym by adding equipment.' : 'No equipment matched your filters.'}

                    </div>

                  )}

                </CardContent>

              </Card>

            </motion.div>



            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.2 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <SectionHeader

                    title="AI suggestions"

                    description="Recommendations tailored to your space, goals, and budget."

                    action={

                      <Button size="sm" variant="outline" onClick={() => router.push('/equipment/suggestions')}>

                        View all

                        <ChevronRight className="ml-1 h-3 w-3" />

                      </Button>

                    }

                  />

                </CardHeader>

                <CardContent>

                  {equipment.suggestions.length > 0 ? (

                    <div className="grid gap-3 md:grid-cols-2">

                      {equipment.suggestions.slice(0, 4).map((suggestion, index) => (

                        <motion.div

                          key={`suggestion-${index}`}

                          className="rounded-2xl border border-border/60 bg-card/70 p-4"

                          initial={{ opacity: 0, y: 12 }}

                          animate={{ opacity: 1, y: 0 }}

                          transition={{ duration: 0.3, delay: index * 0.05 }}

                        >

                          <div className="flex items-start justify-between">

                            <h3 className="text-sm font-semibold">{suggestion.name}</h3>

                            <Badge variant="outline" className="capitalize">{suggestion.category}</Badge>

                          </div>

                          <p className="mt-2 text-xs text-muted-foreground">{suggestion.rationale}</p>

                          <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">

                            <span>Priority: {suggestion.priority}</span>

                            <span>{suggestion.price_range}</span>

                          </div>

                        </motion.div>

                      ))}

                    </div>

                  ) : (

                    <div className="rounded-2xl border border-dashed border-border/60 bg-muted/20 p-6 text-center text-sm text-muted-foreground">

                      AI suggestions will appear after generating a personalised workout plan.

                    </div>

                  )}

                </CardContent>

              </Card>

            </motion.div>



            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.25 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <SectionHeader

                    title="Maintenance planner"

                    description="Keep your equipment in top shape with simple reminders."

                  />

                </CardHeader>

                <CardContent className="space-y-3 text-sm text-muted-foreground">

                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                    Inspect resistance bands monthly for wear and replace any with cracks.

                  </div>

                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                    Wipe down strength equipment after each session to extend lifespan.

                  </div>

                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                    Keep cardio machines calibrated every quarter for accurate metrics.

                  </div>

                </CardContent>

              </Card>

            </motion.div>

          </div>



          <div className="space-y-6">

            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.18 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <CardTitle>Search and filters</CardTitle>

                  <CardDescription>Find the right equipment quickly.</CardDescription>

                </CardHeader>

                <CardContent className="space-y-4">

                  <div>

                    <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Search</p>

                    <input

                      className="w-full rounded-xl border border-border/60 bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"

                      placeholder="Search by name"

                      value={searchQuery}

                      onChange={(event) => setSearchQuery(event.target.value)}

                    />

                  </div>

                  <div>

                    <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Category</p>

                    <div className="flex flex-wrap gap-2">

                      {categories.map((option) => (

                        <Button

                          key={option.value}

                          variant={selectedCategory === option.value ? 'default' : 'outline'}

                          size="sm"

                          onClick={() => setSelectedCategory(option.value)}

                        >

                          {option.label}

                        </Button>

                      ))}

                    </div>

                  </div>

                  <div className="flex items-center justify-between rounded-2xl border border-border/60 bg-muted/20 px-4 py-3 text-sm">

                    <span>Show available only</span>

                    <input

                      type="checkbox"

                      checked={showAvailableOnly}

                      onChange={(event) => setShowAvailableOnly(event.target.checked)}

                    />

                  </div>

                </CardContent>

              </Card>

            </motion.div>



            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.22 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <CardTitle>Quick actions</CardTitle>

                  <CardDescription>Streamline how you manage equipment.</CardDescription>

                </CardHeader>

                <CardContent className="grid grid-cols-2 gap-3">

                  <Button variant="outline" className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4" onClick={handleAddEquipment}>

                    <Plus className="h-5 w-5" />

                    <span className="text-sm">Add item</span>

                  </Button>

                  <Button variant="outline" className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4" onClick={() => router.push('/equipment/suggestions')}>

                    <Sparkles className="h-5 w-5" />

                    <span className="text-sm">AI ideas</span>

                  </Button>

                  <Button variant="outline" className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4" onClick={() => router.push('/settings')}>

                    <Settings className="h-5 w-5" />

                    <span className="text-sm">Preferences</span>

                  </Button>

                  <Button variant="outline" className="h-auto flex flex-col items-center gap-2 rounded-2xl border-border/60 p-4" onClick={() => router.push('/profile/progress')}>

                    <TrendingUp className="h-5 w-5" />

                    <span className="text-sm">View usage</span>

                  </Button>

                </CardContent>

              </Card>

            </motion.div>



            <motion.div

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4, delay: 0.26 }}

            >

              <Card className="border-border/60">

                <CardHeader>

                  <CardTitle>Space planner</CardTitle>

                  <CardDescription>Balance equipment footprint with workout goals.</CardDescription>

                </CardHeader>

                <CardContent className="space-y-3 text-sm text-muted-foreground">

                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                    Keep heavier items against walls to free central floor space for mobility work.

                  </div>

                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                    Stack modular gear inside storage bins for quick access during sessions.

                  </div>

                  <div className="rounded-2xl border border-border/60 bg-muted/20 p-3">

                    Schedule quarterly reviews to retire equipment you no longer use.

                  </div>

                </CardContent>

              </Card>

            </motion.div>

          </div>

        </div>

      </div>



      <MobileBottomNav current="equipment" />

    </div>

  );

}



